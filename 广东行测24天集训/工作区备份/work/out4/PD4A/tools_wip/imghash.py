"""Compute perceptual hashes of embedded images for all pool figure questions; cache to imghash.json"""
import pymupdf, json, sys, os, glob, re, numpy as np, hashlib
from PIL import Image
import io
pymupdf.TOOLS.mupdf_display_errors(False)
sys.path.insert(0,'/home/user/work/out3/PD3A/tools')
import pool
W='/home/user/work'
P=pool.pool()
docs={}
out={}
def dh(im):
    g=np.asarray(im.convert('L').resize((17,16),Image.LANCZOS)).astype(int)
    b=(g[:,1:]>g[:,:-1]).flatten()
    return ''.join('1' if x else '0' for x in b)
idx={}
for p in P:
    tag=p['tag']
    if tag not in idx: idx[tag]={x['qno']:x for x in json.load(open(f'{W}/index/{tag}.json')) if x['kind']=='q'}
    q=idx[tag][p['qno']]
    f=q['file']
    if f not in docs:
        try: docs[f]=pymupdf.open('/home/user/'+f)
        except Exception as e: print('ERR',f,e); continue
    doc=docs[f]; hs=[]
    for (pg,y0,y1) in q['segs']:
        page=doc[pg]
        try: infos=page.get_image_info(xrefs=True)
        except Exception as e: infos=[]
        for info in infos:
            bb=pymupdf.Rect(info['bbox'])
            if bb.y1>y0 and bb.y0<y1 and info['xref'] and bb.width>40 and bb.height>20:
                try:
                    pix=pymupdf.Pixmap(doc,info['xref'])
                    if pix.n-pix.alpha>=4: pix=pymupdf.Pixmap(pymupdf.csRGB,pix)
                    if pix.alpha: pix=pymupdf.Pixmap(pix,0)
                    im=Image.frombytes('RGB' if pix.n==3 else 'L',(pix.width,pix.height),pix.samples)
                    hs.append(dict(h=dh(im),w=pix.width,hh=pix.height,bw=round(bb.width),bh=round(bb.height)))
                except Exception as e:
                    pass
    out[f"{tag}|{p['qno']}"]=hs
json.dump(out,open('imghash.json','w'))
n0=sum(1 for v in out.values() if not v)
print(len(out),'questions; no-embedded-image:',n0)
