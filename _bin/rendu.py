# -*- coding: utf-8 -*-
"""
rendu.py — Rend un aperçu mp4 depuis edl.json (mêmes règles que monter_edl.py :
9:16 -> plein cadre sans flou ; 16:9 -> fit + fond flou). Sert à contrôler le
montage sans ouvrir CapCut.
"""
import os, sys, json, subprocess, tempfile, shutil

W, H = 1080, 1920


def ff():
    c = "_bin/ffmpeg.exe" if os.name == "nt" else "_bin/ffmpeg"
    return os.path.abspath(c) if os.path.exists(c) else __import__("imageio_ffmpeg").get_ffmpeg_exe()


def dims(f, exe):
    r = subprocess.run([exe, "-i", f], stderr=subprocess.PIPE).stderr.decode("utf-8", "ignore")
    import re
    m = re.search(r"Video:.*?, (\d{2,5})x(\d{2,5})", r)
    return (int(m.group(1)), int(m.group(2)))


def main(proj):
    exe = ff()
    edl = json.load(open(os.path.join(proj, "edl.json"), encoding="utf-8"))
    tmp = tempfile.mkdtemp()
    liste = os.path.join(tmp, "liste.txt")
    parts = []
    for i, beat in enumerate(edl["beats"]):
        src, a, b = beat[:3]
        opt = beat[3] if len(beat) > 3 and isinstance(beat[3], dict) else {}
        son = float(opt.get("son", 0.0))   # clip parlé : on garde son audio
        z = float(opt.get("zoom", edl.get("zoom", 1.8)))   # même zoom que CapCut sur les 16:9
        w, h = dims(src, exe)
        dur = b - a
        if h / w >= 1.5:   # vertical -> cover plein cadre, aucun flou
            vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
        else:              # 16:9 -> clip net devant + fond flou (comme CapCut)
            vf = (f"split=2[bg][fg];"
                  f"[bg]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},gblur=sigma=40[b];"
                  f"[fg]scale={int(W * z) // 2 * 2}:-2[f];[b][f]overlay=(W-w)/2:(H-h)/2")
        out = os.path.join(tmp, f"{i:03d}.mp4")
        if son > 0:
            aud = ["-map", "0:v", "-map", "0:a", "-af", f"volume={son},aresample=44100,aformat=channel_layouts=stereo"]
            src_a = []
        else:
            aud = ["-map", "0:v", "-map", "1:a", "-shortest"]
            src_a = ["-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=44100:cl=stereo"]
        subprocess.run([exe, "-y", "-ss", str(a), "-t", str(dur), "-i", src, *src_a,
                        "-vf", vf + f",fps=30,setsar=1", *aud,
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                        "-c:a", "aac", "-b:a", "192k",
                        "-pix_fmt", "yuv420p", out, "-loglevel", "error"], check=True)
        parts.append(out)
        print(f"  plan {i+1}/{len(edl['beats'])}", end="\r")
    with open(liste, "w") as f:
        for p in parts:
            f.write(f"file '{p}'\n")
    muet = os.path.join(tmp, "muet.mp4")
    subprocess.run([exe, "-y", "-f", "concat", "-safe", "0", "-i", liste,
                    "-c", "copy", muet, "-loglevel", "error"], check=True)
    voix = os.path.join(proj, "voix.mp3")
    final = os.path.join(proj, "apercu.mp4")
    subprocess.run([exe, "-y", "-i", muet, "-i", voix, "-filter_complex",
                    "[0:a][1:a]amix=inputs=2:duration=first:normalize=0[a]",
                    "-map", "0:v", "-map", "[a]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    final, "-loglevel", "error"], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n[OK] {final}  ({os.path.getsize(final)/1e6:.1f} Mo)")


if __name__ == "__main__":
    main(sys.argv[1])
