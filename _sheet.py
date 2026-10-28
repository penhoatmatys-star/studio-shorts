import sys,subprocess,os,json
from PIL import Image,ImageDraw
import imageio_ffmpeg;ff=imageio_ffmpeg.get_ffmpeg_exe()
def dur(p):
    r=subprocess.run([ff,"-i",p],capture_output=True,text=True).stderr
    import re;m=re.search(r"Duration: (\d+):(\d+):([\d.]+)",r);return int(m[1])*3600+int(m[2])*60+float(m[3])
src,step,start,end,out=sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),float(sys.argv[4]),sys.argv[5]
d=dur(src);end=min(end,d)
ts=[];t=start
while t<end: ts.append(t);t+=step
W,H=180,320;cols=8;ims=[]
for t in ts:
    f="_t.jpg";subprocess.run([ff,"-y","-loglevel","error","-ss",str(t),"-i",src,"-frames:v","1","-vf",f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2",f])
    try: im=Image.open(f).convert("RGB")
    except: im=Image.new("RGB",(W,H))
    ImageDraw.Draw(im).text((4,4),f"{t:.0f}s",fill=(255,255,0));ims.append(im)
rows=(len(ims)+cols-1)//cols
S=Image.new("RGB",(cols*W,rows*H))
for i,im in enumerate(ims):S.paste(im,((i%cols)*W,(i//cols)*H))
S.save(out);print(src,"dur",round(d),"->",out)
