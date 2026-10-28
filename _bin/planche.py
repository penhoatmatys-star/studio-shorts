# -*- coding: utf-8 -*-
import os, sys, subprocess, re, glob
def _ffmpeg():
    """ffmpeg utilisable sur Windows comme sur macOS."""
    c = "_bin/ffmpeg.exe" if os.name == "nt" else "_bin/ffmpeg"
    if os.path.exists(c):
        return os.path.abspath(c)
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()

ff = _ffmpeg()
proj = sys.argv[1]
d = proj if os.path.isdir(proj) else os.path.join("shorts", proj)
src = os.path.join(d, "_src")
out = os.path.join(d, "_frames")
os.makedirs(out, exist_ok=True)
def dur(f):
    r = subprocess.run([ff,"-i",f], stderr=subprocess.PIPE).stderr.decode("utf-8","ignore")
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r)
    if m:
        h,mn,s=m.groups(); return int(h)*3600+int(mn)*60+float(s)
    return 0
for f in sorted(glob.glob(os.path.join(src,"*.mp4"))):
    name = os.path.splitext(os.path.basename(f))[0]
    D = dur(f) or 12
    # 9 frames repartis -> fps pour ~9 vignettes -> tile 3x3
    fps = max(0.1, 9.0/D)
    o = os.path.join(out, name+".png")
    cmd = [ff,"-y","-i",f,"-vf",f"fps={fps:.4f},scale=320:-1,tile=3x3","-frames:v","1",o]
    r = subprocess.run(cmd, stderr=subprocess.PIPE)
    ok = os.path.exists(o)
    print(f"[{'OK' if ok else 'X'}] {name}  ({D:.1f}s) -> {o if ok else r.stderr.decode('utf-8','ignore')[-120:]}")
