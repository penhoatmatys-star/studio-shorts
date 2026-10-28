# -*- coding: utf-8 -*-
"""
nettoyer.py — Retire les bandeaux (sous-titres incrustés, logos) situés EN BORD
d'image, puis re-remplit le cadre 1080x1920 (règle d'or : jamais de flou sur un
9:16, jamais de texte d'un autre créateur).

Usage :
    python _bin/nettoyer.py <projet> <id>:<bord>:<pourcent> [...]
    python _bin/nettoyer.py shorts/ferran_torres 9HTSc1lgExE:top:16 CbWGDrGiRy4:top:12
"""
import os, sys, subprocess

W, H = 1080, 1920


def _ffmpeg():
    c = "_bin/ffmpeg.exe" if os.name == "nt" else "_bin/ffmpeg"
    if os.path.exists(c):
        return os.path.abspath(c)
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def nettoyer(proj, ident, bord, pct):
    ff = _ffmpeg()
    src = os.path.join(proj, "_src", ident + ".mp4")
    dst = os.path.join(proj, "clips", ident + ".mp4")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    f = pct / 100.0
    if bord == "top":
        crop = f"crop=iw:ih*{1-f:.4f}:0:ih*{f:.4f}"
    elif bord == "bottom":
        crop = f"crop=iw:ih*{1-f:.4f}:0:0"
    else:
        raise SystemExit(f"bord inconnu : {bord}")
    # après recadrage on re-remplit le cadre (cover) : pas de bandes, pas de flou
    vf = f"{crop},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    cmd = [ff, "-y", "-i", src, "-vf", vf, "-an",
           "-c:v", "libx264", "-preset", "medium", "-crf", "17",
           "-pix_fmt", "yuv420p", dst, "-loglevel", "error"]
    subprocess.run(cmd, check=True)
    print(f"[OK] {ident} : {bord} -{pct}% -> {dst}")


if __name__ == "__main__":
    proj = sys.argv[1]
    for spec in sys.argv[2:]:
        i, b, p = spec.split(":")
        nettoyer(proj, i, b, float(p))
