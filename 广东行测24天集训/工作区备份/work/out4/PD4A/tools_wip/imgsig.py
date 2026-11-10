"""Robust signatures: for each pool question, concat embedded images that lie mostly inside the question region, trim, resize to 96x32 -> vector. cache to imgsig.npz"""
import pymupdf, json, sys, os, numpy as np
from PIL import Image, ImageFilter
pymupdf.TOOLS.mupdf_display_errors(False)
sys.path.insert(0,'/home/user/work/out3/PD3A/tools')
import pool
W='/home/user/work'
P=pool.pool(); docs={}; idx={}; keys=[]; sigs=[]; nimg=[]
def trim(a):
    m=a<200; ys,xs=np.where(m)
    if not len(ys): return a
    return a[ys.min():ys.max()+1, xs.min():xs.max()+1]
def sig(im):
    a=trim(np.asarray(im.convert('L')))
    im2=Image.fromarray(a).resize((96,32),Image.BOX).filter(ImageFilter.GaussianBlur(1.2))
    v=np.asarray(im2).astype(float).flatten(); v=v-v.mean(); n=np.linalg.norm(v)
    return v/n if n>0 else v
for p in P:
    tag=p['tag']
    if tag not in idx: idx[tag]={x['qno']:x for x in json.load(open(f'{W}/index/{tag}.json')) if x['kind']=='q'}
    q=idx[tag][p['qno']]; f=q['file']
    if f not in docs:
        try: docs[f]=pymupdf.open('/home/user/'+f)
        except Exception as e: continue
    doc=docs[f]
    for (pg,y0,y1) in q['segs']:
        page=doc[pg]
        try: infos=page.get_image_info(xrefs=True)
        except Exception: infos=[]
        for info in infos:
            bb=pymupdf.Rect(info['bbox'])
            ov=min(bb.y1,y1)-max(bb.y0,y0)
            if info['xref'] and bb.width>60 and bb.height>25 and ov>0.6*bb.height:
                try:
                    pix=pymupdf.Pixmap(doc,info['xref'])
                    if pix.n-pix.alpha>=4: pix=pymupdf.Pixmap(pymupdf.csRGB,pix)
                    if pix.alpha: pix=pymupdf.Pixmap(pix,0)
                    im=Image.frombytes('RGB' if pix.n==3 else 'L',(pix.width,pix.height),pix.samples)
                    keys.append(f"{tag}|{p['qno']}"); sigs.append(sig(im))
                except Exception as e: pass
np.savez('imgsig.npz',keys=np.array(keys),sigs=np.array(sigs))
print(len(keys),'image sigs for',len(set(keys)),'questions of',len(P))
