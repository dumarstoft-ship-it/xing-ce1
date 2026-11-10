"""Stitch source-page crops of several questions into one preview image (for eye verification).
usage: mkcrop.py <out.png> <key> [<key> ...]   key = <tag>-<qno> (tag may end with _xc)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qx import get, crop
from PIL import Image, ImageDraw, ImageFont
SP=os.path.dirname(os.path.abspath(__file__)); os.makedirs(f'{SP}/crops', exist_ok=True)
def one(key, dpi=150):
    tag,q=key.rsplit('-',1); qq=get(tag,int(q))
    p=f'{SP}/crops/{key}_{dpi}.png'
    if not os.path.exists(p): crop(qq,p,dpi=dpi)
    return Image.open(p).convert('RGB')
def stitch(out, keys, width=1240):
    ims=[]
    for k in keys:
        im=one(k)
        if im.width!=width: im=im.resize((width,int(im.height*width/im.width)))
        lab=Image.new('RGB',(width,26),(225,225,225)); d=ImageDraw.Draw(lab); d.text((8,6),k,fill=(0,0,0))
        ims+= [lab,im]
    H=sum(i.height for i in ims); cv=Image.new('RGB',(width,H),'white'); y=0
    for i in ims: cv.paste(i,(0,y)); y+=i.height
    cv.convert('L').save(out, optimize=True); return out, cv.size
if __name__=='__main__':
    print(stitch(sys.argv[1], sys.argv[2:]))
