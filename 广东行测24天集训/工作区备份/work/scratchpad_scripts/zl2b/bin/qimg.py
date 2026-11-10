import json,os,sys,re,unicodedata,pymupdf
sys.path.insert(0,os.path.dirname(__file__))
from render2 import render_material
from qparse import parse
pymupdf.TOOLS.mupdf_display_errors(False)
IDX='/home/user/work/index'; OUT='/home/user/work/out2/ZL2B/assets/q'
def crop_segs(tag,qno,dtext=None):
    d=json.load(open(f'{IDX}/{tag}.json')); f=d[0]['file']
    q=[x for x in d if x['kind']=='q' and int(x['qno'])==qno][0]
    segs=[list(s) for s in q['segs']]
    doc=pymupdf.open('/home/user/'+f)
    if dtext:
        # find the D option text inside segs, cut after it
        for i,(p,y0,y1) in enumerate(segs):
            hits=[r for r in doc[p].search_for(dtext) if y0-2<=r.y0<=y1+2]
            if hits:
                segs=segs[:i]+[[p,y0,hits[-1].y1+4]]
                break
    return f,segs
def make(tag,qno,dtext=None,dpi=170):
    f,segs=crop_segs(tag,qno,dtext)
    im,_=render_material(f,segs,dpi=dpi)
    os.makedirs(OUT,exist_ok=True)
    p=f'{OUT}/{tag}_q{qno}.png'; im.save(p); return p, segs
if __name__=='__main__':
    for a in sys.argv[1:]:
        tag,qn,dt=(a.split('|')+[None])[:3]
        print(make(tag,int(qn),dt))
