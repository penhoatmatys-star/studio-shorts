# -*- coding: utf-8 -*-
"""
sous_titres.py — Écrit la clé "sous_titres" de edl.json à partir de la VO réelle.

Le TEXTE vient de texte.txt (orthographe juste, Whisper écorche les noms), le TIMING vient de
_mots.json (_bin/transcrire.py) : alignement caractère par caractère entre les deux.
Règle Matys (2026-10-08) : UNE SEULE LIGNE à la fois → segments courts (MAX_CAR caractères,
MAX_MOTS mots), coupés aussi sur la ponctuation et les pauses.

Usage : python _bin/sous_titres.py shorts/<projet> [--max-car 18] [--max-mots 4]
"""
import os, sys, json, re, difflib, argparse

# Nombres écrits en lettres dans le script (pour le clone) → chiffres à l'écran
CHIFFRES = [
    (r"\bsept-cinq, cinq-trois\b", "7-5, 5-3"),
    (r"\bcent-deuxième\b", "102e"), (r"\bseptième\b", "7e"), (r"\bhuitième\b", "8e"),
    (r"\bdeuxième\b", "2e"), (r"\bnuméro un\b", "numéro 1"),
    (r"\bdeux cent mille dollars\b", "200\u00a0000\u00a0$"), (r"\bdeux cents points\b", "200 points"),
    (r"\bSix ans\b", "6 ans"),
]


PETITS = {"de", "la", "le", "les", "à", "au", "du", "un", "une", "sa", "son", "qui", "et", "en", "ce", "pour", "dans", "avec", "ne"}


def norm(s):
    s = s.lower().replace("œ", "oe").replace("’", "'")
    return re.sub(r"[^0-9a-zàâäçéèêëîïôöùûüÿ]", "", s)


def aligner(mots_script, mots_vo):
    """Renvoie [(debut, fin)] pour chaque mot du script, via les caractères normalisés."""
    vo_chars, vo_t = [], []
    for w in mots_vo:
        n = norm(w["w"]) or "_"
        for k, c in enumerate(n):
            frac = k / max(1, len(n))
            vo_chars.append(c); vo_t.append(w["a"] + frac * (w["b"] - w["a"]))
    sc_chars, sc_idx = [], []
    for i, w in enumerate(mots_script):
        for c in norm(w):
            sc_chars.append(c); sc_idx.append(i)
    m = difflib.SequenceMatcher(None, sc_chars, vo_chars, autojunk=False)
    t_char = [None] * len(sc_chars)
    for a, b, size in m.get_matching_blocks():
        for k in range(size):
            t_char[a + k] = vo_t[b + k]
    res = []
    for i in range(len(mots_script)):
        ts = [t_char[j] for j in range(len(sc_chars)) if sc_idx[j] == i and t_char[j] is not None]
        res.append((min(ts), max(ts)) if ts else None)
    # mots sans correspondance : interpolés entre voisins
    for i, r in enumerate(res):
        if r is None:
            prev = next((res[j][1] for j in range(i - 1, -1, -1) if res[j]), 0.0)
            nxt = next((res[j][0] for j in range(i + 1, len(res)) if res[j]), prev + 0.3)
            res[i] = (prev, max(prev + 0.05, nxt))
    return res


def main():
    p = argparse.ArgumentParser()
    p.add_argument("projet")
    p.add_argument("--max-car", type=int, default=18)
    p.add_argument("--max-mots", type=int, default=4)
    a = p.parse_args()
    proj = a.projet if os.path.isdir(a.projet) else os.path.join("shorts", a.projet)
    texte = open(os.path.join(proj, "texte.txt"), encoding="utf-8").read()
    for pat, rep in CHIFFRES:
        texte = re.sub(pat, rep, texte)
    mots = []
    for w in texte.split():                      # ponctuation isolée (« : ») collée au mot d'avant
        if not norm(w) and mots:
            mots[-1] += w if w not in ":;!?" else "\u00a0" + w
        else:
            mots.append(w)
    vo = json.load(open(os.path.join(proj, "_mots.json"), encoding="utf-8"))
    times = aligner(mots, vo)

    chunks, cur = [], []
    for i, w in enumerate(mots):
        cand = " ".join(mots[j] for j in cur + [i])
        pause = cur and times[i][0] - times[cur[-1]][1] > 0.35
        if cur and (len(cand) > a.max_car or len(cur) >= a.max_mots or pause):
            report = []
            if (not pause and len(cur) > 1 and mots[cur[-1]].lower() in PETITS
                    and len(mots[cur[-1]] + " " + w) <= a.max_car):
                report = [cur.pop()]                 # pas de ligne qui finit sur « de », « la »…
            chunks.append(cur); cur = report
        cur.append(i)
        if re.search(r"[.,;:!?…]$", w):
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)

    st = []
    for k, c in enumerate(chunks):
        t0 = times[c[0]][0]
        fin_mot = times[c[-1]][1] + 0.12
        nxt = times[chunks[k + 1][0]][0] if k + 1 < len(chunks) else fin_mot + 0.3
        fin = nxt if nxt - fin_mot < 0.45 else fin_mot + 0.2   # enchaîne, sauf vrai blanc (clip parlé)
        txt = " ".join(mots[j] for j in c).rstrip(",;:\u00a0 ")
        st.append({"texte": txt, "t": round(t0, 2), "dur": round(max(0.2, min(max(0.3, fin - t0), nxt - t0)), 2)})

    edl_p = os.path.join(proj, "edl.json")
    edl = json.load(open(edl_p, encoding="utf-8"))
    # jamais en même temps qu'une traduction à l'écran (même hauteur → 2 lignes visibles)
    for tx in edl.get("textes") or []:
        a0, a1 = float(tx["t"]), float(tx["t"]) + float(tx["dur"])
        for x in st:
            b0, b1 = x["t"], x["t"] + x["dur"]
            if b0 < a1 and b1 > a0:
                if b0 >= a0:
                    x["t"] = round(a1 + 0.02, 2); x["dur"] = round(max(0.2, b1 - x["t"]), 2)
                else:
                    x["dur"] = round(max(0.2, a0 - 0.02 - b0), 2)
    edl["sous_titres"] = st
    json.dump(edl, open(edl_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[OK] {len(st)} sous-titres (≤ {a.max_car} car., ≤ {a.max_mots} mots) -> {edl_p}")
    for s in st:
        print(f"  {s['t']:6.2f} +{s['dur']:.2f}  {s['texte']}")


if __name__ == "__main__":
    main()
