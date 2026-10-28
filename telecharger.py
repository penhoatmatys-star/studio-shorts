# -*- coding: utf-8 -*-
"""
telecharger.py — Télécharge des vidéos YouTube en HD (jusqu'à 1080p) pour servir
de sources de clips. Fusionne vidéo + audio via le ffmpeg embarqué (imageio-ffmpeg).

Usage :
    python telecharger.py _source_djoko  <url_ou_id> [<url_ou_id> ...]
    python telecharger.py _source_djoko  DXWC4Sv7HC0 _ZjSL3e15-s

Sort les fichiers dans <dossier>/<id>.mp4 à la meilleure résolution <= MAX_HEIGHT.
"""
import os, sys, shutil, subprocess, json
import yt_dlp, imageio_ffmpeg

MAX_HEIGHT = 2160   # plafond 4K (YouTube fournit 360/480/720/1080/1440/2160 selon la vidéo)


def _ffmpeg_dir():
    """Dossier contenant un ffmpeg utilisable par yt-dlp (nom natif selon l'OS)."""
    os.makedirs("_bin", exist_ok=True)
    nom = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    dst = os.path.join("_bin", nom)
    if not os.path.exists(dst):
        shutil.copy(imageio_ffmpeg.get_ffmpeg_exe(), dst)
        os.chmod(dst, 0o755)
    return os.path.abspath("_bin")


def _dimensions(f):
    """Largeur/hauteur via ffprobe (pas de libmediainfo requise)."""
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    r = subprocess.run([ff, "-i", f], stderr=subprocess.PIPE).stderr.decode("utf-8", "ignore")
    import re as _re
    m = _re.search(r"Video:.*?, (\d{2,5})x(\d{2,5})", r)
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


def telecharger(dossier, urls):
    os.makedirs(dossier, exist_ok=True)
    opts = {
        "outtmpl": os.path.join(dossier, "%(id)s.mp4"),
        # priorité H.264 (avc1) lu nativement par CapCut, sinon meilleure source dispo
        "format": f"bestvideo[height<={MAX_HEIGHT}][vcodec^=avc1]+bestaudio[ext=m4a]/"
                  f"bestvideo[height<={MAX_HEIGHT}][ext=mp4]+bestaudio[ext=m4a]/"
                  f"bestvideo[height<={MAX_HEIGHT}]+bestaudio/best[height<={MAX_HEIGHT}]/best",
        "merge_output_format": "mp4",
        "ffmpeg_location": _ffmpeg_dir(),
        "quiet": True, "noprogress": True, "no_warnings": True, "overwrites": True,
    }
    for u in urls:
        url = u if u.startswith("http") else f"https://www.youtube.com/watch?v={u}"
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
            f = os.path.join(dossier, f"{info['id']}.mp4")
            w, h = _dimensions(f)
            print(f"[OK] {info['id']}: {w}x{h}  {os.path.getsize(f)/1e6:.1f}MB")
        except Exception as e:
            print(f"[X] {u}: {str(e)[:120]}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("Usage : python telecharger.py <dossier> <url_ou_id> [...]")
    telecharger(sys.argv[1], sys.argv[2:])
