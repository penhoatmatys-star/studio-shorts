# -*- coding: utf-8 -*-
import sys, json, os
from faster_whisper import WhisperModel
proj = sys.argv[1]
d = proj if os.path.isdir(proj) else os.path.join("shorts", proj)
mp3 = os.path.join(d, "voix.mp3")
model = WhisperModel("small", device="cpu", compute_type="int8")
# décodage via ffmpeg : le décodeur `av` de faster_whisper plante (metadata_errors) avec la version installée
import subprocess, numpy as np
ff = os.path.join("_bin", "ffmpeg.exe") if os.name == "nt" else "ffmpeg"
pcm = subprocess.run([ff, "-v", "error", "-i", mp3, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                     stdout=subprocess.PIPE, check=True).stdout
audio = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768
segs, info = model.transcribe(audio, language="fr", word_timestamps=True)
mots, txt = [], []
for s in segs:
    txt.append(s.text.strip())
    for w in (s.words or []):
        mots.append({"w": w.word.strip(), "a": round(w.start,2), "b": round(w.end,2)})
with open(os.path.join(d, "_mots.json"), "w", encoding="utf-8") as f:
    json.dump(mots, f, ensure_ascii=False, indent=1)
print("[OK] %d mots -> %s/_mots.json" % (len(mots), d))
print("DUREE ~%.1fs" % (mots[-1]["b"] if mots else 0))
print(" ".join(txt))
