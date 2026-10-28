#!/usr/bin/env python3
"""Studio veille → scripts → production.

Petit serveur local (stdlib uniquement) qui sert l'interface `studio/web/` et
pilote Claude Code en mode headless (`claude -p`) pour :
  - lancer une veille actu sport (rapport JSON + Markdown dans shorts/_veille/) ;
  - écrire au moins 2 scripts pour un sujet validé ;
  - retoucher un script via le chat latéral ;
  - lancer la production complète (VO, clips, montage CapCut) d'après CLAUDE.md.

Lancement :  .venv/Scripts/python.exe studio/serveur.py   →  http://localhost:8765
(l'application de bureau, studio/app.py, l'ouvre dans sa propre fenêtre)
"""
import glob
import json
import os
import re
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, unquote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prompts  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
WEB = os.path.join(ICI, "web")
VEILLE = os.path.join(RACINE, "shorts", "_veille")
ETAT = os.path.join(VEILLE, "studio")
JOBS = os.path.join(ICI, "_jobs")
PORT = int(os.environ.get("STUDIO_PORT", "8765"))

os.makedirs(ETAT, exist_ok=True)
os.makedirs(JOBS, exist_ok=True)
VERROU = threading.Lock()


# --------------------------------------------------------------------------- claude

def binaire_claude():
    """Le CLI Claude Code (installé par le script officiel ou npm ; `claude` dans le PATH)."""
    import shutil
    c = shutil.which("claude")
    if c:
        return c
    for cand in ("~/.local/bin/claude.exe", "~/.claude/local/claude.exe",
                 "~/AppData/Roaming/npm/claude.cmd",
                 "~/.local/bin/claude", "~/.claude/local/claude", "/opt/homebrew/bin/claude",
                 "/usr/local/bin/claude"):  # macOS (poste d'Elian)
        p = os.path.expanduser(cand)
        if os.path.exists(p):
            return p
    return None


def env_propre():
    """Environnement sans les variables d'une session Claude Code parente
    (sinon le CLI essaie de passer par le proxy de la session hôte)."""
    env = {k: v for k, v in os.environ.items()
           if not (k.startswith("CLAUDE_CODE") or k in ("CLAUDECODE", "ANTHROPIC_BASE_URL", "CLAUDE_PID"))}
    env["PATH"] = env.get("PATH", "") + os.pathsep + os.path.join(RACINE, "_bin")
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def statut_auth():
    c = binaire_claude()
    if not c:
        return {"ok": False, "raison": "CLI Claude Code introuvable (installe-le : voir LISEZ-MOI.md)"}
    try:
        r = subprocess.run([c, "auth", "status"], capture_output=True, text=True, encoding="utf-8",
                           env=env_propre(), timeout=20)
        d = json.loads(r.stdout or "{}")
        return {"ok": bool(d.get("loggedIn")), "methode": d.get("authMethod"),
                "commande": "claude auth login"}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "raison": str(e), "commande": "claude auth login"}


def appel_claude(prompt, schema=None, outils="Read,Glob,Grep", timeout=900, modele=None):
    """Appel headless bloquant ; renvoie la sortie structurée (si schema) ou le texte."""
    c = binaire_claude()
    if not c:
        raise RuntimeError("CLI Claude Code introuvable")
    cmd = [c, "-p", prompt, "--output-format", "json", "--no-session-persistence",
           "--allowedTools", outils, "--permission-mode", "dontAsk"]
    if schema:
        cmd += ["--json-schema", json.dumps(schema)]
    if modele:
        cmd += ["--model", modele]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=RACINE,
                       env=env_propre(), timeout=timeout)
    try:
        d = json.loads(r.stdout)
    except ValueError:
        raise RuntimeError((r.stderr or r.stdout or "réponse vide")[-800:])
    if d.get("is_error"):
        raise RuntimeError(d.get("result") or "erreur Claude")
    if schema:
        so = d.get("structured_output")
        if so is None:
            so = extraire_json(d.get("result", ""))
        return so
    return d.get("result", "")


def extraire_json(texte):
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", texte, re.S)
    brut = m.group(1) if m else texte[texte.find("{"): texte.rfind("}") + 1]
    return json.loads(brut)


# --------------------------------------------------------------------------- jobs

def nouveau_job(type_, titre, meta=None):
    jid = datetime.now().strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:4]
    job = {"id": jid, "type": type_, "titre": titre, "statut": "en_cours",
           "debut": time.time(), "fin": None, "erreur": None, "resultat": None,
           "meta": meta or {}}
    sauver_job(job)
    return job


def sauver_job(job):
    with open(os.path.join(JOBS, job["id"] + ".json"), "w") as f:
        json.dump(job, f, ensure_ascii=False, indent=1)


def lire_job(jid):
    p = os.path.join(JOBS, os.path.basename(jid) + ".json")
    if not os.path.exists(p):
        return None
    with open(p) as f:
        job = json.load(f)
    # Un job agent dont le process est mort sans finir → on le marque.
    pid = job.get("meta", {}).get("pid")
    if job["statut"] == "en_cours" and pid and not pid_vivant(pid):
        fin = resume_flux(job["id"]).get("final")
        job["statut"] = "termine" if fin and not fin.get("is_error") else "erreur"
        job["fin"] = time.time()
        if job["statut"] == "erreur":
            job["erreur"] = (fin or {}).get("result") or "le process s'est arrêté"
        else:
            job["resultat"] = fin.get("result")
        sauver_job(job)
    return job


WINDOWS = os.name == "nt"


def pid_vivant(pid):
    try:
        if not WINDOWS:
            os.kill(pid, 0)
            return True
        r = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True)
        return str(pid) in r.stdout
    except Exception:  # noqa: BLE001
        return False


def job_thread(job, fonction):
    def run():
        try:
            job["resultat"] = fonction()
            job["statut"] = "termine"
        except Exception as e:  # noqa: BLE001
            job["statut"] = "erreur"
            job["erreur"] = str(e)[-1500:]
        job["fin"] = time.time()
        sauver_job(job)
    threading.Thread(target=run, daemon=True).start()
    return job


def job_agent(job, prompt, outils_mode="bypassPermissions", reprendre=None):
    """Lance un agent Claude Code long (veille, production) détaché du serveur :
    il survit à un redémarrage du serveur, son flux stream-json va dans un .log."""
    c = binaire_claude()
    log = open(os.path.join(JOBS, job["id"] + ".log"), "w")
    cmd = [c, "-p", prompt, "--output-format", "stream-json", "--verbose"]
    if reprendre:  # même session que la production : l'agent garde tout son contexte
        cmd += ["--resume", reprendre]
    cmd += ["--dangerously-skip-permissions"] if outils_mode == "bypassPermissions" \
        else ["--permission-mode", outils_mode]
    detache = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if WINDOWS else {"start_new_session": True}
    p = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, cwd=RACINE,
                         env=env_propre(), **detache)
    job["meta"]["pid"] = p.pid
    sauver_job(job)

    def attendre():
        p.wait()
        lire_job(job["id"])  # finalise le statut
        apres = job["meta"].get("apres")
        if apres in ("veille", "veille_jour"):
            finaliser_veille(job["id"])
        if apres == "veille_jour" and os.path.exists(os.path.join(VEILLE, job["meta"]["veille"] + ".json")):
            scripts_du_jour(job["meta"]["veille"])
        elif apres == "modif":
            finaliser_modif(job["id"])
    threading.Thread(target=attendre, daemon=True).start()
    return job


_FLUX = {}


def resume_flux(jid, depuis=0):
    """Transforme le stream-json d'un agent en lignes lisibles pour l'interface.
    Lecture incrémentale : les journaux de production pèsent des dizaines de Mo."""
    p = os.path.join(JOBS, os.path.basename(jid) + ".log")
    if not os.path.exists(p):
        return {"lignes": [], "final": None, "n": 0, "session": None}
    c = _FLUX.setdefault(jid, {"pos": 0, "reste": b"", "lignes": [], "final": None, "session": None})
    if os.path.getsize(p) < c["pos"]:  # fichier réécrit
        c.update(pos=0, reste=b"", lignes=[], final=None, session=None)
    with open(p, "rb") as f:
        f.seek(c["pos"])
        neuf = f.read()
    c["pos"] += len(neuf)
    morceaux = (c["reste"] + neuf).split(b"\n")
    c["reste"] = morceaux.pop()
    for brut in morceaux:
        brut = brut.decode("utf-8", "replace")
        try:
            ev = json.loads(brut)
        except ValueError:
            if brut.strip():
                c["lignes"].append({"t": "brut", "x": brut[:400]})
            continue
        c["session"] = ev.get("session_id") or c["session"]
        if ev.get("type") == "assistant":
            for b in ev.get("message", {}).get("content", []):
                if b.get("type") == "text" and b.get("text", "").strip():
                    c["lignes"].append({"t": "texte", "x": b["text"].strip()})
                elif b.get("type") == "tool_use":
                    k, x = decrire_outil(b)
                    c["lignes"].append({"t": "outil", "k": k, "x": x})
        elif ev.get("type") == "result":
            c["final"] = ev
    return {"lignes": c["lignes"][depuis:], "n": len(c["lignes"]), "final": c["final"],
            "session": c["session"]}


def decrire_outil(b):
    """(type d'outil, description courte) : l'interface choisit l'icône d'après le type."""
    nom, inp = b.get("name", "?"), b.get("input", {}) or {}
    if nom == "Bash":
        return "bash", inp.get("description") or inp.get("command", "")[:140]
    if nom in ("Read", "Write", "Edit"):
        chemin = (inp.get("file_path") or "").replace(RACINE + os.sep, "").replace(RACINE + "/", "")
        return nom.lower(), chemin
    if nom == "WebSearch":
        return "search", inp.get("query", "")
    if nom == "WebFetch":
        return "web", inp.get("url", "")
    return "autre", nom


# --------------------------------------------------------------------------- veilles

def lister_veilles():
    noms = set()
    for p in glob.glob(os.path.join(VEILLE, "*.md")) + glob.glob(os.path.join(VEILLE, "*.json")):
        noms.add(os.path.splitext(os.path.basename(p))[0])
    sortie = []
    for n in sorted(noms, reverse=True):
        js = os.path.join(VEILLE, n + ".json")
        item = {"id": n, "json": os.path.exists(js), "md": os.path.exists(os.path.join(VEILLE, n + ".md"))}
        if item["json"]:
            try:
                with open(js) as f:
                    d = json.load(f)
                item["tldr"] = d.get("tldr", "")
                item["nb"] = len(d.get("sujets", []))
                item["top"] = max([s.get("note", 0) for s in d.get("sujets", [])] or [0])
            except Exception:  # noqa: BLE001
                item["json"] = False
        sortie.append(item)
    return sortie


def lire_veille(vid):
    vid = os.path.basename(vid)
    js, md = os.path.join(VEILLE, vid + ".json"), os.path.join(VEILLE, vid + ".md")
    d = {"id": vid}
    if os.path.exists(js):
        with open(js) as f:
            d.update(json.load(f))
    if os.path.exists(md):
        with open(md) as f:
            d["markdown"] = f.read()
    d["etat"] = lire_etat(vid)
    return d


def finaliser_veille(jid):
    job = lire_job(jid)
    if job and job["statut"] == "termine":
        job["meta"]["veilles"] = [v["id"] for v in lister_veilles()[:1]]
        sauver_job(job)


def lire_etat(vid):
    p = os.path.join(ETAT, os.path.basename(vid) + ".json")
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return {}


def ecrire_etat(vid, etat):
    with VERROU:
        with open(os.path.join(ETAT, os.path.basename(vid) + ".json"), "w") as f:
            json.dump(etat, f, ensure_ascii=False, indent=1)


def maj_sujet(vid, sid, **champs):
    with VERROU:
        p = os.path.join(ETAT, os.path.basename(vid) + ".json")
        etat = {}
        if os.path.exists(p):
            with open(p) as f:
                etat = json.load(f)
        s = etat.setdefault(sid, {})
        s.update(champs)
        with open(p, "w") as f:
            json.dump(etat, f, ensure_ascii=False, indent=1)
        return s


def trouver_sujet(vid, sid):
    v = lire_veille(vid)
    for s in v.get("sujets", []):
        if s.get("id") == sid:
            return v, s
    raise KeyError("sujet introuvable : %s/%s" % (vid, sid))


# --------------------------------------------------------------------------- actions

def action_veille(corps):
    """Veille à la demande. corps.quotidien : formule du jour (4 sujets d'1 min dont 3 tennis et
    1 foot, 5 sujets de 25-30 s), puis un script écrit pour chaque sujet."""
    quotidien = bool(corps.get("quotidien"))
    moment = "jour" if quotidien else (corps.get("moment") or ("matin" if datetime.now().hour < 14 else "soir"))
    nom = datetime.now().strftime("%Y-%m-%d_") + moment
    if os.path.exists(os.path.join(VEILLE, nom + ".json")) and not corps.get("forcer"):
        nom = datetime.now().strftime("%Y-%m-%d_%Hh%M")
    suite = "veille_jour" if quotidien and not corps.get("bloquant") else "veille"
    job = nouveau_job("veille", ("Veille du jour " if quotidien else "Veille ") + nom,
                      {"apres": suite, "veille": nom})
    return job_agent(job, prompts.prompt_veille(nom, corps.get("consigne", ""), quotidien))


def synchro_git():
    """Veilles partagées par Git : récupère celle écrite dans le cloud chaque matin et envoie
    l'état local (sujets validés, scripts, retouches). Seul shorts/_veille/ est commité ici."""
    import shutil
    git = shutil.which("git")
    if not git or not os.path.isdir(os.path.join(RACINE, ".git")):
        return "pas de dépôt git"

    def g(*args):
        return subprocess.run([git, *args], cwd=RACINE, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=120)
    with VERROU:
        g("add", "shorts/_veille")
        if g("diff", "--cached", "--quiet").returncode:
            g("commit", "-q", "-m", "veille : état du studio (%s)" % os.environ.get("USERNAME", os.environ.get("USER", "?")))
        r = g("pull", "--rebase", "--autostash", "-q")
        if r.returncode:
            g("rebase", "--abort")
            return "pull impossible : " + (r.stderr or r.stdout)[-300:]
    r = g("push", "-q")
    return "ok" if r.returncode == 0 else "push impossible : " + (r.stderr or r.stdout)[-300:]


def veille_du_jour_faite():
    return os.path.exists(os.path.join(VEILLE, datetime.now().strftime("%Y-%m-%d_jour.json")))


def veille_en_cours():
    """Une veille tourne déjà (lancée par l'app ou par la tâche planifiée) ?"""
    for p in sorted(glob.glob(os.path.join(JOBS, "*.json")), reverse=True)[:40]:
        try:
            with open(p) as f:
                j = json.load(f)
        except (OSError, ValueError):
            continue
        if j.get("type") == "veille" and j.get("statut") == "en_cours" and (lire_job(j["id"]) or {}).get("statut") == "en_cours":
            return True
    return False


def veille_du_jour_bloquante():
    """Pour la tâche planifiée (studio/quotidien.py) : veille du jour puis scripts, en attendant
    la fin de chaque étape. Ne fait rien si la veille du jour existe déjà (y compris celle
    écrite dans le cloud, récupérée d'abord par git)."""
    synchro_git()
    if veille_du_jour_faite():
        return "veille du jour déjà faite"
    job = action_veille({"quotidien": True, "bloquant": True})
    while (lire_job(job["id"]) or {}).get("statut") == "en_cours":
        time.sleep(10)
    vid = job["meta"]["veille"]
    if not os.path.exists(os.path.join(VEILLE, vid + ".json")):
        return "veille ratée : " + str((lire_job(job["id"]) or {}).get("erreur"))
    return "veille %s : %d script(s) écrits" % (vid, scripts_du_jour(vid))


def scripts_du_jour(vid):
    """Après la veille du jour : un script par sujet, au bon format (1 min ou 25-30 s).
    Deux à la fois pour ne pas saturer le compte Claude ; bloquant (appelé dans un thread)."""
    from concurrent.futures import ThreadPoolExecutor
    v = lire_veille(vid)
    sujets = [s for s in v.get("sujets", []) if not lire_etat(vid).get(s["id"], {}).get("scripts")]

    def un(s):
        e = lire_etat(vid).get(s["id"], {})  # relu : l'app et la tâche planifiée peuvent tourner ensemble
        if e.get("scripts") or (e.get("job_scripts") and (lire_job(e["job_scripts"]) or {}).get("statut") == "en_cours"):
            return
        job = action_scripts({"veille": vid, "sujet": s["id"], "nombre": 1, "auto": True})
        while (lire_job(job["id"]) or {}).get("statut") == "en_cours":
            time.sleep(5)
    with ThreadPoolExecutor(2) as pool:
        list(pool.map(un, sujets))
    return len(sujets)


def action_convertir(corps):
    """Rapport Markdown ancien format → JSON lisible par l'interface."""
    vid = os.path.basename(corps["veille"])
    md = os.path.join(VEILLE, vid + ".md")
    job = nouveau_job("convertir", "Conversion " + vid, {"veille": vid})

    def f():
        d = appel_claude(prompts.prompt_conversion(md), schema=prompts.SCHEMA_VEILLE)
        d["id"] = vid
        with open(os.path.join(VEILLE, vid + ".json"), "w") as fo:
            json.dump(d, fo, ensure_ascii=False, indent=1)
        return {"veille": vid}
    return job_thread(job, f)


def action_scripts(corps):
    vid, sid = corps["veille"], corps["sujet"]
    v, s = trouver_sujet(vid, sid)
    if not corps.get("auto"):  # script écrit d'office par la veille du jour : sujet pas encore validé
        maj_sujet(vid, sid, valide=True)
    job = nouveau_job("scripts", "Scripts : " + s.get("titre", sid), {"veille": vid, "sujet": sid})
    maj_sujet(vid, sid, job_scripts=job["id"])

    def f():
        d = appel_claude(prompts.prompt_scripts(v, s, corps.get("consigne", ""),
                                                int(corps.get("nombre", 3))),
                         schema=prompts.SCHEMA_SCRIPTS,
                         outils=prompts.OUTILS_SCRIPT, timeout=2400)
        scripts = d.get("scripts", [])
        for sc in scripts:
            sc["id"] = uuid.uuid4().hex[:6]
            sc["mots"] = compter_mots(sc.get("texte", ""))
            sc["chat"] = []
        etat = lire_etat(vid).get(sid, {})
        anciens = etat.get("scripts", []) if corps.get("ajouter") else []
        maj_sujet(vid, sid, scripts=anciens + scripts)
        return {"n": len(scripts)}
    return job_thread(job, f)


def action_chat(corps):
    vid, sid, scid, message = corps["veille"], corps["sujet"], corps["script"], corps["message"]
    v, s = trouver_sujet(vid, sid)
    etat = lire_etat(vid).get(sid, {})
    sc = next(x for x in etat.get("scripts", []) if x["id"] == scid)
    if corps.get("texte"):  # l'utilisateur a pu retoucher le texte à la main
        sc["texte"] = corps["texte"]
    sc.setdefault("chat", []).append({"role": "moi", "x": message, "t": time.time()})
    sc["chat_attente"] = True
    maj_sujet(vid, sid, scripts=etat["scripts"])
    job = nouveau_job("chat", "Retouche", {"veille": vid, "sujet": sid, "script": scid})

    def f():
        try:
            d = appel_claude(prompts.prompt_chat(s, sc, message), schema=prompts.SCHEMA_CHAT,
                             outils=prompts.OUTILS_SCRIPT, timeout=900)
        except Exception as e:  # noqa: BLE001
            d = {"reponse": "⚠️ " + str(e)[-400:], "texte": None}
        etat2 = lire_etat(vid).get(sid, {})
        sc2 = next(x for x in etat2["scripts"] if x["id"] == scid)
        if d.get("texte"):
            sc2.setdefault("versions", []).append(sc2["texte"])
            sc2["texte"] = d["texte"]
            sc2["mots"] = compter_mots(d["texte"])
        sc2.setdefault("chat", []).append({"role": "ia", "x": d.get("reponse", ""),
                                           "modifie": bool(d.get("texte")), "t": time.time()})
        sc2["chat_attente"] = False
        maj_sujet(vid, sid, scripts=etat2["scripts"])
        return d
    return job_thread(job, f)


def action_maj_script(corps):
    vid, sid = corps["veille"], corps["sujet"]
    etat = lire_etat(vid).get(sid, {})
    for sc in etat.get("scripts", []):
        if sc["id"] == corps["script"]:
            if "texte" in corps:
                if corps["texte"] != sc["texte"]:
                    sc.setdefault("versions", []).append(sc["texte"])
                sc["texte"] = corps["texte"]
                sc["mots"] = compter_mots(sc["texte"])
            if corps.get("annuler") and sc.get("versions"):
                sc["texte"] = sc["versions"].pop()
                sc["mots"] = compter_mots(sc["texte"])
    champs = {"scripts": etat.get("scripts", [])}
    if "choisi" in corps:
        champs["choisi"] = corps["choisi"]
    return maj_sujet(vid, sid, **champs)


def action_production(corps):
    vid, sid, scid = corps["veille"], corps["sujet"], corps["script"]
    v, s = trouver_sujet(vid, sid)
    etat = lire_etat(vid).get(sid, {})
    sc = next(x for x in etat["scripts"] if x["id"] == scid)
    projet = re.sub(r"[^a-z0-9_]+", "_", (corps.get("projet") or sid).lower()).strip("_")
    dossier = os.path.join(RACINE, "shorts", projet)
    if os.path.exists(os.path.join(dossier, "edl.json")) and not corps.get("forcer"):
        raise ValueError("shorts/%s existe déjà avec un montage : choisis un autre nom." % projet)
    os.makedirs(dossier, exist_ok=True)
    corps.setdefault("options", {}).setdefault("format", s.get("format") or "long")
    with open(os.path.join(dossier, "script_studio.md"), "w") as f:
        f.write("# %s\n\n%s\n" % (sc.get("titre", ""), sc["texte"]))
    with open(os.path.join(dossier, "brief.json"), "w") as f:
        json.dump({"veille": vid, "sujet": s, "script": sc, "options": corps.get("options", {})},
                  f, ensure_ascii=False, indent=1)
    if corps.get("modele_parfait"):
        ajouter_modele(s, sc)
    job = nouveau_job("production", "Production : " + projet,
                      {"veille": vid, "sujet": sid, "script": scid, "projet": projet})
    maj_sujet(vid, sid, choisi=scid, production={"job": job["id"], "projet": projet,
                                                 "jobs": [job["id"]], "chat": []})
    return job_agent(job, prompts.prompt_production(projet, corps.get("options", {})))


def lister_productions():
    """Tous les montages (en cours, puis récents) pour le panneau latéral du studio :
    un élément par projet = son dernier job (production ou modification)."""
    par_projet = {}
    titres = {}
    for chemin in sorted(glob.glob(os.path.join(JOBS, "*.json"))):
        try:
            with open(chemin) as f:
                brut = json.load(f)
        except (OSError, ValueError):
            continue
        if brut.get("type") != "production" or not brut.get("meta", {}).get("projet"):
            continue
        job = lire_job(brut["id"])  # finalise un job dont le process est mort
        m = job["meta"]
        flux = resume_flux(job["id"])
        lignes = flux["lignes"]
        derniere = next((l["x"] for l in reversed(lignes) if l["t"] in ("outil", "texte")), "")
        cle = (m.get("veille"), m.get("sujet"))
        if cle not in titres:
            try:
                titres[cle] = trouver_sujet(*cle)[1].get("titre", "")
            except Exception:  # noqa: BLE001
                titres[cle] = ""
        par_projet[m["projet"]] = {
            "job": job["id"], "projet": m["projet"], "veille": m.get("veille"), "sujet": m.get("sujet"),
            "titre": titres[cle], "statut": job["statut"], "debut": job["debut"], "fin": job["fin"],
            "modif": m.get("apres") == "modif", "demande": m.get("demande"),
            "etapes": flux["n"], "derniere": derniere[:220], "erreur": (job.get("erreur") or "")[:200],
        }
    items = list(par_projet.values())
    maintenant = time.time()
    items = [x for x in items if x["statut"] == "en_cours" or maintenant - (x["fin"] or 0) < 3 * 86400]
    items.sort(key=lambda x: (x["statut"] != "en_cours", -(x["fin"] or x["debut"])))
    return items


def maj_prod(vid, sid, fonction):
    """Modifie l'état de production d'un sujet sous verrou."""
    with VERROU:
        p = os.path.join(ETAT, os.path.basename(vid) + ".json")
        with open(p) as f:
            etat = json.load(f)
        prod = etat[sid]["production"]
        prod.setdefault("chat", [])
        prod.setdefault("jobs", [prod["job"]])
        fonction(prod)
        with open(p, "w") as f:
            json.dump(etat, f, ensure_ascii=False, indent=1)
        return prod


def action_prod_chat(corps):
    """Chat de l'écran Production.
    - montage en cours : un assistant observe (lecture seule) et répond ; une demande de
      changement devient une consigne dans _consignes.md, que l'agent relit entre ses étapes ;
    - montage fini : on reprend la session de l'agent (--resume) pour appliquer la demande."""
    vid, sid, message = corps["veille"], corps["sujet"], corps["message"].strip()
    _, s = trouver_sujet(vid, sid)
    prod = lire_etat(vid)[sid]["production"]
    projet = prod["projet"]
    job = lire_job(prod["job"])
    maj_prod(vid, sid, lambda p: p["chat"].append({"role": "moi", "x": message, "t": time.time()}))

    if job and job["statut"] == "en_cours":
        maj_prod(vid, sid, lambda p: p.update(chat_attente=True))
        flux = resume_flux(job["id"])
        journal = "\n".join(l["x"] for l in flux["lignes"][-80:])
        chat = lire_etat(vid)[sid]["production"]["chat"]

        def f():
            try:
                d = appel_claude(prompts.prompt_prod_observateur(projet, s, journal, chat, message),
                                 schema=prompts.SCHEMA_PROD_CHAT, outils="Read,Glob,Grep", timeout=300)
            except Exception as e:  # noqa: BLE001
                d = {"reponse": "⚠️ " + str(e)[-300:], "consigne": None}
            if d.get("consigne"):
                with open(os.path.join(RACINE, "shorts", projet, "_consignes.md"), "a") as fo:
                    fo.write("- [%s] %s\n" % (datetime.now().strftime("%H:%M"), d["consigne"]))

            def ajout(p):
                p["chat"].append({"role": "ia", "x": d.get("reponse", ""), "consigne": d.get("consigne"),
                                  "t": time.time()})
                p["chat_attente"] = False
            maj_prod(vid, sid, ajout)
            return d
        return job_thread(nouveau_job("chat_prod", "Question production", {"veille": vid, "sujet": sid}), f)

    # montage terminé (ou arrêté) : on relance l'agent sur sa propre session
    session = None
    for jid in reversed(prod.get("jobs", [prod["job"]])):
        session = resume_flux(jid).get("session")
        if session:
            break
    nouveau = nouveau_job("production", "Modification : " + projet,
                          {"veille": vid, "sujet": sid, "projet": projet, "apres": "modif",
                           "demande": message})

    def bascule(p):
        p["job"] = nouveau["id"]
        p["jobs"].append(nouveau["id"])
        p["chat_attente"] = True
    maj_prod(vid, sid, bascule)
    return job_agent(nouveau, prompts.prompt_prod_modif(projet, message, bool(session)), reprendre=session)


def finaliser_modif(jid):
    job = lire_job(jid)
    vid, sid = job["meta"]["veille"], job["meta"]["sujet"]
    texte = job.get("resultat") or ("⚠️ " + (job.get("erreur") or "la modification s'est arrêtée"))

    def ajout(p):
        p["chat"].append({"role": "ia", "x": texte, "modifie": job["statut"] == "termine", "t": time.time()})
        p["chat_attente"] = False
    maj_prod(vid, sid, ajout)


def action_recherche(corps):
    """Barre de recherche : Matys propose son propre sujet, Claude le documente comme un sujet
    de veille (faits, vidéos, citations, hooks…) et l'ajoute en tête de la veille affichée."""
    texte = (corps.get("texte") or "").strip()
    if len(texte) < 3:
        raise ValueError("Écris un sujet un peu plus précis.")
    vid = os.path.basename(corps.get("veille") or "")
    if not (vid and os.path.exists(os.path.join(VEILLE, vid + ".json"))):
        vid = datetime.now().strftime("%Y-%m-%d_perso")
    job = nouveau_job("recherche", "Recherche : " + texte, {"veille": vid, "texte": texte})

    def f():
        sujet = appel_claude(prompts.prompt_recherche(texte), schema=prompts.SCHEMA_SUJET,
                             outils="WebSearch,WebFetch,Read,Glob,Grep", timeout=1500)
        sujet["perso"] = True
        sujet["demande"] = texte
        return {"veille": vid, "sujet": ajouter_sujet(vid, sujet)}
    return job_thread(job, f)


def slug(t):
    t = t.lower()
    for a, b in (("àâä", "a"), ("éèêë", "e"), ("îï", "i"), ("ôö", "o"), ("ùûü", "u"), ("ç", "c")):
        for x in a:
            t = t.replace(x, b)
    return re.sub(r"[^a-z0-9]+", "_", t).strip("_")[:40] or "sujet"


def ajouter_sujet(vid, sujet):
    """Ajoute un sujet en tête de la veille `vid` (créée si besoin) ; renvoie son id unique."""
    with VERROU:
        p = os.path.join(VEILLE, vid + ".json")
        if os.path.exists(p):
            with open(p) as fo:
                v = json.load(fo)
        else:
            v = {"id": vid, "titre": "Mes sujets — " + datetime.now().strftime("%d/%m/%Y"),
                 "date": datetime.now().strftime("%Y-%m-%d"), "moment": "perso",
                 "tldr": "Tes sujets : recherches et scripts envoyés depuis le studio.", "sujets": []}
        ids = {x.get("id") for x in v.get("sujets", [])}
        base = slug(sujet.get("id") or sujet.get("titre") or "sujet")
        sid, i = base, 2
        while sid in ids:
            sid, i = "%s_%d" % (base, i), i + 1
        sujet["id"] = sid
        v.setdefault("sujets", []).insert(0, sujet)
        with open(p, "w") as fo:
            json.dump(v, fo, ensure_ascii=False, indent=1)
    return sid


def action_mon_script(corps):
    """« J'ai mon script » : Matys colle un script tout prêt → sujet + script dans le studio,
    puis (au choix) montage lancé tout de suite ou ouverture dans l'atelier."""
    texte = (corps.get("texte") or "").strip()
    if compter_mots(texte) < 30:
        raise ValueError("Le script est trop court (moins de 30 mots).")
    titre = (corps.get("titre") or "").strip() or texte.split("\n")[0][:80]
    projet = slug(corps.get("projet") or titre)
    if corps.get("lancer") and os.path.exists(os.path.join(RACINE, "shorts", projet, "edl.json")):
        raise ValueError("shorts/%s existe déjà avec un montage : choisis un autre nom de projet." % projet)
    vid = datetime.now().strftime("%Y-%m-%d_perso")
    resume = re.sub(r"\[[^\]]*\]", "", texte).strip().replace("\n", " ")
    sujet = {"id": projet, "titre": titre, "note": None, "verdict": "go", "perso": True,
             "format": "court" if compter_mots(texte) < 180 else "long",  # 25-30 s ≈ 110-130 mots
             "script_perso": True, "resume": resume[:220] + ("…" if len(resume) > 220 else ""),
             "contexte": (corps.get("contexte") or "").strip(),
             "faits": [], "videos": [], "sources": [], "fiabilite": "partiel",
             "fiabilite_detail": "Script fourni par Matys : faits à vérifier pendant la production."}
    sid = ajouter_sujet(vid, sujet)
    sc = {"id": uuid.uuid4().hex[:6], "titre": "Ton script", "mecanisme": "Script écrit par Matys",
          "texte": texte, "mots": compter_mots(texte), "chat": []}
    maj_sujet(vid, sid, valide=True, scripts=[sc], choisi=sc["id"])
    if corps.get("lancer"):
        action_production({"veille": vid, "sujet": sid, "script": sc["id"], "projet": projet,
                           "options": corps.get("options") or {}})
    return {"veille": vid, "sujet": sid, "script": sc["id"], "projet": projet,
            "lance": bool(corps.get("lancer"))}


def ajouter_modele(s, sc):
    with open(os.path.join(RACINE, "scripts_modeles.md"), "a") as f:
        f.write("\n\n---\n\n## %s (studio, %s)\n\n%s\n" % (
            s.get("titre", ""), datetime.now().strftime("%Y-%m-%d"), sc["texte"]))


def compter_mots(t):
    t = re.sub(r"\[[^\]]*\]", " ", t or "")  # les [CLIP …] ne sont pas dits par la VO
    return len(re.findall(r"[\wÀ-ÿ'’-]+", t))


def arreter_job(jid):
    job = lire_job(jid)
    pid = job and job.get("meta", {}).get("pid")
    if pid and pid_vivant(pid):
        if WINDOWS:
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True)
        else:
            import signal
            os.killpg(pid, signal.SIGTERM)  # l'agent a sa propre session (start_new_session)
        job["statut"] = "arrete"
        job["fin"] = time.time()
        sauver_job(job)
    return job


# --------------------------------------------------------------------------- HTTP

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def envoyer(self, code, corps, type_="application/json; charset=utf-8"):
        if not isinstance(corps, (bytes, bytearray)):
            corps = json.dumps(corps, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", type_)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(corps)))
        self.end_headers()
        self.wfile.write(corps)

    def envoyer_video(self, p):
        """Sert l'aperçu par morceaux (Range) : la lecture et l'avance rapide marchent."""
        taille = os.path.getsize(p)
        debut, fin = 0, taille - 1
        m = re.match(r"bytes=(\d*)-(\d*)", self.headers.get("Range") or "")
        if m:
            debut = int(m.group(1) or 0)
            fin = min(int(m.group(2)) if m.group(2) else taille - 1, taille - 1)
        n = fin - debut + 1
        self.send_response(206 if m else 200)
        self.send_header("Content-Type", "video/mp4")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(n))
        if m:
            self.send_header("Content-Range", "bytes %d-%d/%d" % (debut, fin, taille))
        self.end_headers()
        try:
            with open(p, "rb") as f:
                f.seek(debut)
                while n > 0:
                    bloc = f.read(min(n, 1 << 20))
                    if not bloc:
                        break
                    self.wfile.write(bloc)
                    n -= len(bloc)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):
        u = urlparse(self.path)
        ch = unquote(u.path)
        try:
            if ch == "/api/auth":
                return self.envoyer(200, statut_auth())
            if ch == "/api/version":
                web = [os.path.getmtime(os.path.join(WEB, x)) for x in os.listdir(WEB)]
                return self.envoyer(200, {"v": int(max(web))})
            if ch == "/api/veilles":
                return self.envoyer(200, lister_veilles())
            if ch.startswith("/api/veille/"):
                return self.envoyer(200, lire_veille(ch.split("/")[-1]))
            if ch.startswith("/api/job/"):
                jid = ch.split("/")[3]
                job = lire_job(jid)
                if not job:
                    return self.envoyer(404, {"erreur": "job inconnu"})
                depuis = int((u.query.split("depuis=")[1:] or ["0"])[0] or 0)
                job["flux"] = resume_flux(jid, depuis) if job.get("meta", {}).get("pid") else None
                return self.envoyer(200, job)
            if ch == "/api/productions":
                return self.envoyer(200, lister_productions())
            if ch == "/api/jobs":
                js = sorted(glob.glob(os.path.join(JOBS, "*.json")), reverse=True)[:30]
                return self.envoyer(200, [lire_job(os.path.basename(p)[:-5]) for p in js])
            if ch.startswith("/apercu/"):  # vidéo d'aperçu d'un projet
                p = os.path.join(RACINE, "shorts", os.path.basename(ch.split("/")[2]), "apercu.mp4")
                if os.path.exists(p):
                    return self.envoyer_video(p)
                return self.envoyer(404, {"erreur": "pas d'aperçu"})
            # fichiers statiques
            nom = "index.html" if ch in ("/", "") else ch.lstrip("/")
            p = os.path.normpath(os.path.join(WEB, nom))
            if not p.startswith(WEB) or not os.path.isfile(p):
                return self.envoyer(404, {"erreur": "introuvable"})
            types = {".html": "text/html", ".js": "text/javascript", ".css": "text/css",
                     ".svg": "image/svg+xml", ".woff2": "font/woff2", ".png": "image/png"}
            with open(p, "rb") as f:
                return self.envoyer(200, f.read(),
                                    types.get(os.path.splitext(p)[1], "application/octet-stream") + "; charset=utf-8")
        except Exception as e:  # noqa: BLE001
            return self.envoyer(500, {"erreur": str(e)})

    def do_POST(self):
        ch = urlparse(self.path).path
        n = int(self.headers.get("Content-Length") or 0)
        try:
            corps = json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            return self.envoyer(400, {"erreur": "JSON invalide"})
        routes = {
            "/api/veille": action_veille,
            "/api/convertir": action_convertir,
            "/api/scripts": action_scripts,
            "/api/chat": action_chat,
            "/api/script": action_maj_script,
            "/api/production": action_production,
            "/api/prod_chat": action_prod_chat,
            "/api/recherche": action_recherche,
            "/api/mon_script": action_mon_script,
            "/api/arreter": lambda c: arreter_job(c["job"]),
        }
        if ch not in routes:
            return self.envoyer(404, {"erreur": "route inconnue"})
        try:
            return self.envoyer(200, routes[ch](corps))
        except Exception as e:  # noqa: BLE001
            return self.envoyer(400, {"erreur": str(e)})


def serveur_http(port=PORT):
    """Le serveur, écoute seulement en local (127.0.0.1) ; utilisé aussi par app.py."""
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    print("Studio : http://localhost:%d" % PORT, flush=True)
    serveur_http().serve_forever()
