"""rr.py TAG Q [Q...] : render questions (keep opts) at 130dpi into r/ and make a vertical contact sheet r/sheet_TAG_Qs.png"""
import sys, os
sys.path.insert(0,'/home/user/work/out2/PD2A/tools')
from rq import render
from PIL import Image, ImageDraw
tag=sys.argv[1]; qs=[int(x) for x in sys.argv[2:] if x.isdigit()]
dpi=130
for a in sys.argv[2:]:
    if a.startswith('dpi='): dpi=int(a[4:])
ims=[]
for q in qs:
    try:
        p=render(tag,q,f'r/{tag}_{q}.png',dpi,keep_opts=True)
        im=Image.open(p).convert('RGB')
    except Exception as e:
        print('ERR',tag,q,e); continue
    lab=Image.new('RGB',(im.width,22),(255,255,200)); ImageDraw.Draw(lab).text((4,4),f'{tag}-{q}',fill=(200,0,0))
    ims+= [lab,im]
W=max(i.width for i in ims); H=sum(i.height for i in ims)
c=Image.new('RGB',(W,H),'white'); y=0
for i in ims: c.paste(i,(0,y)); y+=i.height
out=f"r/sheet_{tag}_{'_'.join(map(str,qs))}.png"; c.save(out); print(out,c.size)
