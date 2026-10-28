# -*- coding: utf-8 -*-
"""
telecharger_images.py — récupère les vraies photos d'incrustation (trouvées sur Google Images)
et les convertit en JPG lisible par CapCut.

Usage :
    python telecharger_images.py shorts/<projet> <nom>=<url_image> [<nom>=<url_image> ...]
    ex : python telecharger_images.py shorts/france_belgique olise=https://.../olise.jpg

Sortie : shorts/<projet>/images/<nom>.jpg  (+ taille affichée ; < 400 px = à remplacer)
"""
import os, sys, subprocess, urllib.request, imageio_ffmpeg

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
FF = imageio_ffmpeg.get_ffmpeg_exe()


def telecharger(dossier, nom, url):
    os.makedirs(dossier, exist_ok=True)
    tmp = os.path.join(dossier, f"_{nom}.tmp")
    out = os.path.join(dossier, f"{nom}.jpg")
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r, open(tmp, "wb") as f:
        f.write(r.read())
    # webp/png/avif -> jpg (CapCut + pyJianYingDraft lisent le jpg sans surprise)
    p = subprocess.run([FF, "-y", "-loglevel", "error", "-i", tmp, "-frames:v", "1", "-q:v", "2", out],
                       capture_output=True, text=True)
    os.remove(tmp)
    if p.returncode:
        raise RuntimeError(p.stderr.strip()[:200] or "pas une image")
    info = subprocess.run([FF, "-i", out], capture_output=True, text=True).stderr
    taille = next((w for w in info.split() if "x" in w and w.split("x")[0].isdigit()), "?").rstrip(",")
    w = int(taille.split("x")[0]) if taille != "?" else 0
    return out, taille, w


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    dossier = os.path.join(sys.argv[1], "images")
    for arg in sys.argv[2:]:
        nom, _, url = arg.partition("=")
        try:
            out, taille, w = telecharger(dossier, nom, url)
            print(f"[OK] {nom}.jpg {taille}" + ("  <- trop petite, en chercher une autre" if w < 400 else ""))
        except Exception as e:
            print(f"[X] {nom} : {e}")
