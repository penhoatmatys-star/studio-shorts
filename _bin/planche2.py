# -*- coding: utf-8 -*-
import sys, os, subprocess, imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
f, start, end, tag = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
dur = end - start
n = 35
fps = n/dur
out = os.path.join(os.path.dirname(os.path.dirname(f)), "_frames", tag + "_zoom.jpg")
vf = (r"fps=%f,scale=300:-1,drawtext=text='%%{eif\:(t+%g)\:d}.%%{eif\:(mod(t+%g,1)*10)\:d}':x=4:y=4:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.7,tile=5x7" % (fps, start, start))
cmd = [ff, "-y", "-ss", str(start), "-i", f, "-t", str(dur), "-vf", vf, "-frames:v", "1", "-q:v", "3", out]
r = subprocess.run(cmd, stderr=subprocess.PIPE)
print(("[OK] " if os.path.exists(out) else "[X] ")+out)
if not os.path.exists(out): print(r.stderr.decode("utf-8","ignore")[-300:])
