# -*- coding: utf-8 -*-
"""
generer_voix.py — Génère la voix off `voix.mp3` à partir d'un texte, avec le
clone vocal ElevenLabs de Matys (API HTTP, pas besoin du SDK).

Config (créée automatiquement au 1er lancement si absente) :
    _voix_clone/elevenlabs.json
        {
          "api_key":  "<ta clé API ElevenLabs>",
          "voice_id": "<l'ID de ton clone>",
          "model_id": "eleven_multilingual_v2",
          "voice_settings": {"stability":0.35,"similarity_boost":0.85,
                             "style":0.35,"use_speaker_boost":true}
        }
    (la clé peut aussi venir de la variable d'env ELEVENLABS_API_KEY)

Usage :
    # depuis un projet : lit shorts/<projet>/texte.txt -> shorts/<projet>/voix.mp3
    python generer_voix.py algerie_autriche

    # texte libre -> fichier précis
    python generer_voix.py --texte "Salut, ceci est un test." --out test.mp3
    python generer_voix.py --fichier mon_script.txt --out voix.mp3

Réglages voix (façon "short" Max Parra) : stability bas = plus expressif/punchy.
À ajuster dans le JSON après 2-3 essais.
"""
import os, sys, json, shutil, subprocess, argparse, re

try:                       # console Windows : éviter les crashs d'encodage
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

CONFIG_PATH = os.path.join("_voix_clone", "elevenlabs.json")
API_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
OUTPUT_FORMAT = "mp3_44100_128"   # 44.1 kHz / 128 kbps

CONFIG_TEMPLATE = {
    "api_key": "COLLE_TA_CLE_API_ICI",
    "voice_id": "COLLE_L_ID_DE_TON_CLONE_ICI",
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
        "stability": 0.35,
        "similarity_boost": 0.85,
        "style": 0.35,
        "use_speaker_boost": True,
    },
}


def charger_config():
    if not os.path.exists(CONFIG_PATH):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(CONFIG_TEMPLATE, f, indent=2, ensure_ascii=False)
        sys.exit(
            f"[CONFIG] Fichier créé : {CONFIG_PATH}\n"
            f"  -> Ouvre-le et renseigne 'api_key' et 'voice_id', puis relance."
        )
    with open(CONFIG_PATH, encoding="utf-8") as f:
        cfg = json.load(f)
    cfg["api_key"] = os.environ.get("ELEVENLABS_API_KEY", cfg.get("api_key", "")).strip()
    if not cfg["api_key"] or cfg["api_key"].startswith("COLLE_"):
        sys.exit(f"[CONFIG] Renseigne 'api_key' dans {CONFIG_PATH} (ou ELEVENLABS_API_KEY).")
    if not cfg.get("voice_id") or cfg["voice_id"].startswith("COLLE_"):
        sys.exit(f"[CONFIG] Renseigne 'voice_id' dans {CONFIG_PATH}.")
    return cfg


def resoudre_io(args):
    """Détermine (texte, chemin_sortie) selon les arguments."""
    if args.texte:
        return args.texte.strip(), (args.out or "voix.mp3")
    if args.fichier:
        with open(args.fichier, encoding="utf-8") as f:
            return f.read().strip(), (args.out or "voix.mp3")
    # mode projet
    projet = args.projet
    dossier = projet if os.path.isdir(projet) else os.path.join("shorts", projet)
    texte_path = os.path.join(dossier, "texte.txt")
    if not os.path.exists(texte_path):
        sys.exit(f"[X] Introuvable : {texte_path}")
    with open(texte_path, encoding="utf-8") as f:
        return f.read().strip(), (args.out or os.path.join(dossier, "voix.mp3"))


def nettoyer_texte(t):
    """Retire les lignes vides multiples ; garde la ponctuation (= respirations)."""
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def appliquer_corrections(t, cfg):
    """Remplace certains mots par une orthographe phonétique AVANT la synthèse,
    pour corriger la prononciation du clone (ex. Autriche -> Otriche).
    N'altère PAS texte.txt : ne touche que ce qui est envoyé à ElevenLabs.
    Table dans elevenlabs.json -> "corrections_phonetiques": {"mot":"phonetique"}."""
    for mot, remplacement in (cfg.get("corrections_phonetiques") or {}).items():
        t = re.sub(rf"\b{re.escape(mot)}\b", remplacement, t, flags=re.IGNORECASE)
    return t


def alleger_ponctuation(t, cfg):
    """Retire les virgules et les points de suspension AVANT la synthèse, pour
    éviter les micro-pauses (débit plus enchaîné). N'altère PAS texte.txt.
    Désactivable via "supprimer_virgules": false dans elevenlabs.json."""
    if not cfg.get("supprimer_virgules", True):
        return t
    t = t.replace("…", " ").replace("...", " ")
    t = t.replace(",", "")
    return re.sub(r"[ \t]{2,}", " ", t)


def duree_mp3(path):
    try:
        import imageio_ffmpeg
        ff = imageio_ffmpeg.get_ffmpeg_exe()
        out = subprocess.run([ff, "-i", path], stderr=subprocess.PIPE).stderr.decode("utf-8", "ignore")
        m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", out)
        if m:
            h, mn, s = m.groups()
            return int(h) * 3600 + int(mn) * 60 + float(s)
    except Exception:
        pass
    return None


def retirer_respirations(path, cfg):
    """Coupe les respirations et blancs entre les mots, comme à la main dans CapCut.
    Whisper donne la position de chaque mot ; tout ce qui est HORS des mots (+ petites marges)
    est supprimé quand le blanc dépasse `seuil`, remplacé par un silence court. La voix n'est
    jamais touchée : si une zone coupée contient du niveau de parole, l'alerte est affichée."""
    import numpy as np, imageio_ffmpeg
    from faster_whisper import WhisperModel
    SR = 44100
    AVANT, APRES = cfg.get("marge_avant", 0.03), cfg.get("marge_apres", 0.07)   # marges gardées autour d'un mot
    SEUIL, SILENCE = cfg.get("blanc_max", 0.14), cfg.get("blanc_garde", 0.06)    # blanc > SEUIL -> coupé, SILENCE gardé
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    raw = subprocess.run([ff, "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         stdout=subprocess.PIPE, check=True).stdout
    x = np.frombuffer(raw, np.float32).copy()
    seg, _ = WhisperModel("small", compute_type="int8").transcribe(path, language="fr", word_timestamps=True)
    mots = [(w.start, w.end) for s in seg for w in s.words]
    if not mots:
        return
    dur = len(x) / SR
    zones = [[max(0, mots[0][0] - AVANT), mots[0][1] + APRES]]
    for (a0, b0), (a, b) in zip(mots, mots[1:]):
        if a - b0 <= SEUIL:                      # petit blanc naturel : audio d'origine conservé
            zones[-1][1] = b + APRES
        else:
            zones.append([a - AVANT, b + APRES])
    zones[-1][1] = min(dur, zones[-1][1] + 0.1)
    for z, nxt in zip(zones, zones[1:]):         # marges qui se chevauchent
        z[1] = min(z[1], nxt[0])

    def souffle(i):                              # trame de 10 ms bruitée et peu forte = respiration
        fr = x[i:i + 441]
        if len(fr) < 441:
            return False
        d = 20 * np.log10(np.sqrt(np.mean(fr ** 2)) + 1e-9)
        sp = np.abs(np.fft.rfft(fr * np.hanning(441)))[5:] + 1e-9
        return -48 < d < -26 and np.exp(np.mean(np.log(sp))) / np.mean(sp) > 0.2

    def niv(i):                                  # niveau en dB d'une trame de 10 ms
        fr = x[max(i, 0):max(i, 0) + 441]
        return 20 * np.log10(np.sqrt(np.mean(fr ** 2)) + 1e-9) if len(fr) else -99

    for z in zones:                              # Whisper donne des fins de mots trop tôt : on suit l'énergie réelle
        i, n = int(z[1] * SR), 0
        while niv(i) > -42 and not souffle(i) and n < 30:
            i += 441; n += 1
        z[1] = min(dur, i / SR)
        i, n = int(z[0] * SR) - 441, 0
        while i > 0 and niv(i) > -42 and not souffle(i) and n < 15:
            i -= 441; n += 1
        z[0] = max(0, (i + 441) / SR)
    for z, nxt in zip(zones, zones[1:]):
        z[1] = min(z[1], nxt[0])

    MIN = int(cfg.get("souffle_min", 0.18) * 100)    # un souffle dure plus qu'une consonne (s, f, ch)
    for z in zones:                              # souffle collé au début/à la fin d'une zone gardée
        i, n = int(z[1] * SR) - 441, 0
        while i > 0 and souffle(i) and n < 60:
            i -= 441; n += 1
        if n >= MIN:
            z[1] -= (n - 1) * 0.01
        i, n = int(z[0] * SR), 0
        while souffle(i) and n < 60:
            i += 441; n += 1
        if n >= MIN:
            z[0] += (n - 1) * 0.01
    f, morceaux, alertes, retire = int(0.008 * SR), [], 0, 0.0
    for k, (s, e) in enumerate(zones):
        c = x[int(s * SR):int(e * SR)].copy()
        if len(c) > 2 * f:
            c[:f] *= np.linspace(0, 1, f); c[-f:] *= np.linspace(1, 0, f)
        morceaux.append(c)
        if k + 1 < len(zones):
            morceaux.append(np.zeros(int(SILENCE * SR), np.float32))
            trou = x[int(e * SR):int(zones[k + 1][0] * SR)]
            retire += len(trou) / SR - SILENCE
            if cfg.get("debug_respirations"):
                fr = [trou[i:i + 441] for i in range(0, len(trou) - 441, 441)] or [trou]
                lv = [20 * np.log10(np.sqrt(np.mean(c ** 2)) + 1e-9) for c in fr]
                fl = [np.exp(np.mean(np.log(np.abs(np.fft.rfft(c * np.hanning(len(c))))[5:] + 1e-9))) / np.mean(np.abs(np.fft.rfft(c * np.hanning(len(c))))[5:] + 1e-9) for c in fr]
                print(f"[RESP-DBG] {e:6.2f}-{zones[k + 1][0]:6.2f}s ({len(trou) / SR:4.2f}s) max {max(lv):5.1f} dB  trames>-35dB: {sum(v > -35 for v in lv)}  platitude moy {np.mean(fl):.2f}")
            if len(trou) > 960 and max(20 * np.log10(np.sqrt(np.mean(trou[i:i + 960] ** 2)) + 1e-9)
                                       for i in range(0, len(trou) - 960, 480)) > -22:
                alertes += 1
                print(f"[RESP] ATTENTION : niveau de voix dans le trou coupé à {e:.2f}s")
    y = np.concatenate(morceaux)
    tmp = path + ".resp.mp3"
    subprocess.run([ff, "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-c:a", "libmp3lame", "-b:a", "128k", tmp], input=y.tobytes(), check=True)
    shutil.move(tmp, path)
    print(f"[RESP] {len(zones) - 1} blancs/respirations coupés, {retire:.1f}s retirées, {alertes} alerte(s)")


def compresser_pauses(path, cfg):
    """Ramène chaque silence (< seuil dB) de plus de `pause_min` à EXACTEMENT `pause_cible` s
    (défaut 0,10 s). Les micro-blancs naturels entre mots, plus courts, ne bougent pas.
    Désactivable via "pause_cible": 0 dans elevenlabs.json."""
    import numpy as np, imageio_ffmpeg
    cible = float(cfg.get("pause_cible", 0.10))
    if cible <= 0:
        return
    seuil, minrun, SR = cfg.get("pause_seuil_db", -42), cfg.get("pause_min", 0.10), 44100
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    x = np.frombuffer(subprocess.run([ff, "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                     stdout=subprocess.PIPE, check=True).stdout, np.float32).copy()
    n = int(0.01 * SR); m = len(x) // n
    db = 20 * np.log10(np.sqrt((x[:m * n].reshape(m, n) ** 2).mean(1)) + 1e-9)
    sil, parts, i, nk, gagne = db < seuil, [], 0, 0, 0.0
    while i < m:
        j = i
        if sil[i]:
            while j < m and sil[j]:
                j += 1
            L = (j - i) * 0.01
            if L >= minrun and i > 0 and j < m:
                keep = int(round(cible / 0.01)); a = keep // 2
                parts += [x[i * n:(i + a) * n], x[(j - (keep - a)) * n:j * n]]; nk += 1; gagne += L - cible
            else:
                parts.append(x[i * n:j * n])
        else:
            while j < m and not sil[j]:
                j += 1
            parts.append(x[i * n:j * n])
        i = j
    tmp = path + ".pause.mp3"
    subprocess.run([ff, "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-c:a", "libmp3lame", "-b:a", "128k", tmp], input=np.concatenate(parts).tobytes(), check=True)
    shutil.move(tmp, path)
    print(f"[PAUSE] {nk} pauses ramenées à {cible:.2f}s ({gagne:.1f}s gagnées)")


def nettoyer_audio(path, cfg):
    """Coupe les respirations (noise gate) + raccourcit les silences entre phrases.
    Désactivable via "nettoyer_respirations": false dans elevenlabs.json.
    Réglable via "filtre_audio" (chaîne -af ffmpeg)."""
    if not cfg.get("nettoyer_respirations", True):
        return
    if cfg.get("retirer_respirations", True):
        try:
            retirer_respirations(path, cfg)
        except Exception as e:                    # pas de Whisper : on garde le filtre ffmpeg seul
            print("[RESP] ignoré :", e)
    compresser_pauses(path, cfg)
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    af = cfg.get(
        "filtre_audio",
        # 1) gate : tout ce qui est < ~-34 dB (respirations, bruit de bouche) -> coupé
        "agate=threshold=0.02:ratio=4:attack=5:release=120,"
        # 2) silenceremove : enlève les blancs > 0.45 s (rythme plus sec, façon short)
        "silenceremove=stop_periods=-1:stop_duration=0.45:stop_threshold=-38dB",
    )
    tmp = path + ".clean.mp3"
    cmd = [ff, "-y", "-i", path, "-af", af, "-c:a", "libmp3lame", "-b:a", "128k", tmp]
    r = subprocess.run(cmd, stderr=subprocess.PIPE)
    if r.returncode == 0 and os.path.exists(tmp):
        shutil.move(tmp, path)
        print("[CLEAN] respirations coupées + silences resserrés")
    else:
        if os.path.exists(tmp):
            os.remove(tmp)
        print("[CLEAN] filtre ignoré :", r.stderr.decode("utf-8", "ignore")[-160:])


def generer(texte, sortie, cfg):
    import requests
    texte = nettoyer_texte(texte)
    nb_mots = len(re.findall(r"\w+", texte))
    texte = appliquer_corrections(texte, cfg)
    texte = alleger_ponctuation(texte, cfg)
    print(f"[TTS] {nb_mots} mots  ->  {sortie}")
    print(f"      modèle={cfg['model_id']}  voice={cfg['voice_id'][:8]}…  réglages={cfg['voice_settings']}")

    url = API_URL.format(voice_id=cfg["voice_id"])
    r = requests.post(
        url,
        params={"output_format": OUTPUT_FORMAT},
        headers={"xi-api-key": cfg["api_key"], "Content-Type": "application/json"},
        json={
            "text": texte,
            "model_id": cfg["model_id"],
            "voice_settings": cfg["voice_settings"],
        },
        timeout=180,
    )
    if r.status_code != 200:
        sys.exit(f"[X] ElevenLabs {r.status_code} : {r.text[:300]}")

    os.makedirs(os.path.dirname(os.path.abspath(sortie)), exist_ok=True)
    # sauvegarde une éventuelle voix.mp3 existante (enregistrée à la main)
    if os.path.exists(sortie):
        bak = sortie + ".bak"
        shutil.copy(sortie, bak)
        print(f"      (ancienne voix sauvegardée : {bak})")
    with open(sortie, "wb") as f:
        f.write(r.content)

    nettoyer_audio(sortie, cfg)

    d = duree_mp3(sortie)
    taille = os.path.getsize(sortie) / 1e6
    info_d = f"{d:.1f}s" if d else "?"
    print(f"[OK] {sortie}  ({taille:.2f} MB, {info_d})")
    if d:
        print(f"     ≈ {nb_mots/max(d,1):.1f} mots/s  (cible Max Parra ~4)")


def convertir_prise(prise, sortie, cfg):
    """Voice Changer : ta prise brute (téléphone OK) -> même intonation, voix studio du clone.
    Facturé à la durée (~1000 crédits/min) : la prise est d'abord resserrée (blancs coupés)."""
    import requests, imageio_ffmpeg
    if not os.path.exists(prise):
        sys.exit(f"[X] Prise introuvable : {prise}")
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    serree = sortie + ".prise.mp3"
    subprocess.run([ff, "-y", "-v", "error", "-i", prise, "-ac", "1", "-af",
                    "silenceremove=start_periods=1:start_threshold=-45dB:"
                    "stop_periods=-1:stop_duration=0.35:stop_threshold=-45dB",
                    "-b:a", "192k", serree], check=True)
    print(f"[STS] {prise} ({duree_mp3(serree) or 0:.1f}s envoyées)  ->  {sortie}")
    reglages = cfg.get("sts_voice_settings") or {
        k: v for k, v in cfg["voice_settings"].items() if k != "speed"}
    with open(serree, "rb") as f:
        r = requests.post(
            f"https://api.elevenlabs.io/v1/speech-to-speech/{cfg['voice_id']}",
            params={"output_format": OUTPUT_FORMAT},
            headers={"xi-api-key": cfg["api_key"]},
            data={"model_id": cfg.get("sts_model_id", "eleven_multilingual_sts_v2"),
                  "voice_settings": json.dumps(reglages),
                  "remove_background_noise": "true"},
            files={"audio": f},
            timeout=300,
        )
    os.remove(serree)
    if r.status_code != 200:
        sys.exit(f"[X] ElevenLabs {r.status_code} : {r.text[:300]}")
    if os.path.exists(sortie):
        shutil.copy(sortie, sortie + ".bak")
    with open(sortie, "wb") as f:
        f.write(r.content)
    nettoyer_audio(sortie, cfg)
    print(f"[OK] {sortie}  ({duree_mp3(sortie) or 0:.1f}s)")


def main():
    p = argparse.ArgumentParser(description="Génère voix.mp3 avec le clone ElevenLabs.")
    p.add_argument("projet", nargs="?", help="nom du projet (shorts/<projet>) ou chemin dossier")
    p.add_argument("--texte", help="texte brut à dire (au lieu d'un projet)")
    p.add_argument("--fichier", help="fichier .txt à dire")
    p.add_argument("--prise", help="Voice Changer : ta prise audio brute à convertir")
    p.add_argument("--out", help="chemin de sortie .mp3")
    p.add_argument("--nettoyer", help="retire seulement les respirations d'un mp3 existant (copie .avant_nettoyage gardée)")
    args = p.parse_args()
    if args.nettoyer:
        shutil.copy(args.nettoyer, args.nettoyer + ".avant_nettoyage")
        nettoyer_audio(args.nettoyer, charger_config())
        return
    if not (args.projet or args.texte or args.fichier or args.prise):
        p.error("donne un <projet>, ou --texte, ou --fichier, ou --prise")
    cfg = charger_config()
    if args.prise:
        dossier = (args.projet if os.path.isdir(args.projet or "") else
                   os.path.join("shorts", args.projet)) if args.projet else "."
        convertir_prise(args.prise, args.out or os.path.join(dossier, "voix.mp3"), cfg)
        return
    texte, sortie = resoudre_io(args)
    generer(texte, sortie, cfg)


if __name__ == "__main__":
    main()
