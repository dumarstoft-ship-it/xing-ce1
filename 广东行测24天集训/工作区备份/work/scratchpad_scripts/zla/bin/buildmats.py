import json, os, re, sys, unicodedata, pymupdf
from PIL import Image
pymupdf.TOOLS.mupdf_display_errors(False)
sys.path.insert(0, os.path.dirname(__file__))
from matspec import MATS
from render2 import render_material
IDX='/home/user/work/index'
OUTPREV='/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zla/matprev'
os.makedirs(OUTPREV, exist_ok=True)
JUNK=re.compile(r'(本试卷由粉笔用户|认准淘宝店铺|网友回忆版\)\s*$|^第\s*\d+\s*页|^-\s*\d+\s*-$|^\d+$|TB:Seeyee|行测》题\(|行测》真题|公务员录用考试《行测》)')
def file_of(tag): return json.load(open(f'{IDX}/{tag}.json'))[0]['file']
def render(path, segs, dpi=200, margin_x=20):
    doc=pymupdf.open('/home/user/'+path); ims=[]; texts=[]
    for (p,y0,y1) in segs:
        page=doc[p]
        clip=pymupdf.Rect(margin_x, max(0,y0), page.rect.width-margin_x, min(page.rect.height,y1))
        pix=page.get_pixmap(clip=clip, dpi=dpi)
        ims.append(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
        texts.append(page.get_text('text', clip=clip))
    W=max(i.width for i in ims); H=sum(i.height for i in ims)
    c=Image.new('RGB',(W,H),'white'); y=0
    for i in ims: c.paste(i,(0,y)); y+=i.height
    return c, '\n'.join(texts)
def clean(t):
    t=unicodedata.normalize('NFKC',t)
    lines=[l.strip() for l in t.split('\n')]
    lines=[l for l in lines if l and not JUNK.search(l)]
    return '\n'.join(lines)
if __name__=='__main__':
    only=set(sys.argv[1:])
    for m in MATS:
        if only and m['mid'] not in only: continue
        f=file_of(m['tag'])
        im,txt=render_material(f, m['segs'])
        im.save(f"{OUTPREV}/{m['mid']}.png")
        open(f"{OUTPREV}/{m['mid']}.txt",'w').write(clean(txt))
        print(m['mid'], im.size, len(txt))
