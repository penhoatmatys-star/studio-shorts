"""Aide au placement de la flèche d'intro : image du 1er plan (cadrée comme dans CapCut, 1080×1920)
avec la zone sûre TikTok / YouTube Shorts et la position actuelle de la flèche.

    .venv/Scripts/python.exe _bin/fleche.py shorts/<projet>            -> _frames/fleche.png
    .venv/Scripts/python.exe _bin/fleche.py shorts/<projet> -0.2 0.35  -> essaie une position

Regarder l'image (Read), viser le joueur, puis écrire "fleche_xy": [x, y] dans edl.json.
Repère : x de -1 (gauche) à 1 (droite), y de -1 (bas) à 1 (haut), centre = 0.
"""
import json
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)
from monter_edl import FLECHE_XY, FLECHE_ZONE, dans_zone_sure  # noqa: E402

W, H = 1080, 1920


def px(x, y):
    return (x + 1) / 2 * W, (1 - y) / 2 * H


def main(projet, xy=None):
    edl = json.load(open(os.path.join(projet, "edl.json"), encoding="utf-8"))
    src, a, b = edl["beats"][0][:3]
    ffmpeg = next((p for p in (os.path.join(RACINE, "_bin", "ffmpeg.exe"), os.path.join(RACINE, "_bin", "ffmpeg"))
                   if os.path.exists(p)), shutil.which("ffmpeg"))
    sortie = os.path.join(projet, "_frames", "fleche.png")
    os.makedirs(os.path.dirname(sortie), exist_ok=True)
    t = a + min(0.4, (b - a) / 2)   # la flèche est à l'écran dès le début du 1er plan
    subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-ss", str(t), "-i", src, "-frames:v", "1",
                    "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}", sortie], check=True)

    x, y = xy or edl.get("fleche_xy", FLECHE_XY)
    xs, ys = dans_zone_sure(x, y)
    img = Image.open(sortie).convert("RGB")
    voile = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(voile)
    (x0, x1), (y0, y1) = FLECHE_ZONE["x"], FLECHE_ZONE["y"]
    gauche, haut = px(x0, y1)
    droite, bas = px(x1, y0)
    for boite in ((0, 0, W, haut), (0, bas, W, H), (0, haut, gauche, bas), (droite, haut, W, bas)):
        d.rectangle(boite, fill=(255, 40, 40, 90))   # zones masquées par l'interface TikTok / Shorts
    cx, cy = px(xs, ys)
    d.ellipse((cx - 60, cy - 60, cx + 60, cy + 60), outline=(255, 140, 40, 255), width=8)
    d.line((cx - 90, cy, cx + 90, cy), fill=(255, 140, 40, 255), width=4)
    d.line((cx, cy - 90, cx, cy + 90), fill=(255, 140, 40, 255), width=4)
    img = Image.alpha_composite(img.convert("RGBA"), voile).convert("RGB")
    img.resize((W // 2, H // 2)).save(sortie)
    recale = "" if (xs, ys) == (x, y) else f" (demandé ({x}, {y}), recalé dans la zone sûre)"
    print(f"{sortie} : flèche en ({xs:.2f}, {ys:.2f}){recale}. Rouge = caché par TikTok/Shorts.")


if __name__ == "__main__":
    if len(sys.argv) not in (2, 4):
        sys.exit(__doc__)
    main(sys.argv[1], (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) == 4 else None)
