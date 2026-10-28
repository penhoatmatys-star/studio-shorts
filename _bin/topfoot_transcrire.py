# -*- coding: utf-8 -*-
"""Transcrit les vidéos d'un compte TikTok listé par veille_tiktok.py, par vues décroissantes.
python _bin/topfoot_transcrire.py topfoot_youss [N]   (reprend où il s'est arrêté)
Sortie : shorts/_veille_tiktok/<handle>_scripts/<id>.txt ; interprète : .venv (faster_whisper)."""
import sys, json, os, subprocess, pathlib, tempfile
import numpy as np
from faster_whisper import WhisperModel

h = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 400
root = pathlib.Path(__file__).resolve().parent.parent
out = root / "shorts" / "_veille_tiktok" / f"{h}_scripts"; out.mkdir(exist_ok=True)
vids = sorted(json.load(open(root / "shorts" / "_veille_tiktok" / f"{h}.json", encoding="utf-8")), key=lambda x: -x["vues"])[:N]
vids = [v for v in vids if (v["duree"] or 0) <= 120]
ff = str(root / "_bin" / "ffmpeg.exe")
ytdlp = str(root / ".venv312" / "Scripts" / "yt-dlp.exe")
model = WhisperModel("small", device="cpu", compute_type="int8")
tmp = pathlib.Path(tempfile.mkdtemp())
if os.environ.get("REV"): vids = vids[::-1]
for i, v in enumerate(vids):
    f = out / f"{v['id']}.txt"
    if f.exists(): continue
    try: os.close(os.open(str(f.with_suffix('.lck')), os.O_CREAT | os.O_EXCL))
    except FileExistsError: continue
    mp4 = tmp / f"{v['id']}.mp4"
    r = subprocess.run([ytdlp, "-q", "--ffmpeg-location", ff, "-o", str(mp4), v["url"]], capture_output=True, text=True)
    if not mp4.exists():
        print(i, v["id"], "download KO", r.stderr[-150:], flush=True); continue
    pcm = subprocess.run([ff, "-v", "error", "-i", str(mp4), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         stdout=subprocess.PIPE).stdout
    mp4.unlink()
    audio = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768
    segs, _ = model.transcribe(audio, language="fr", vad_filter=True)
    f.write_text(" ".join(s.text.strip() for s in segs), encoding="utf-8")
    print(i, v["id"], v["vues"], flush=True)
