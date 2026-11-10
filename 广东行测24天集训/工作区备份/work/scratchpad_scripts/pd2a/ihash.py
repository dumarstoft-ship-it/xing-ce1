import json, os, sys, numpy as np, pymupdf
from PIL import Image
pymupdf.TOOLS.mupdf_display_errors(False)
IDX='/home/user/work/index'
inv=json.load(open('inv.json'))
cache={}
def getq(tag,qno):
    if tag not in cache:
        cache[tag]={q['qno']:q for q in json.load(open(f'{IDX}/{tag}.json')) if q['kind']=='q'}
    return cache[tag].get(qno)
docs={}
def hashq(q):
    if not q['images']: return None
    # union of images on the first page that has the largest image
    best=max(q['images'], key=lambda im:(im[1][2]-im[1][0])*(im[1][3]-im[1][1]))
    p=best[0]
    ims=[im for im in q['images'] if im[0]==p]
    x0=min(i[1][0] for i in ims); y0=min(i[1][1] for i in ims); x1=max(i[1][2] for i in ims); y1=max(i[1][3] for i in ims)
    f=q['file']
    if f not in docs: docs[f]=pymupdf.open('/home/user/'+f)
    page=docs[f][p]
    clip=pymupdf.Rect(x0,y0,x1,y1)&page.rect
    if clip.is_empty or clip.width<5 or clip.height<5: return None
    pix=page.get_pixmap(clip=clip,dpi=60,colorspace=pymupdf.csGRAY)
    a=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width)
    m=a<200
    if m.sum()<10: return None
    ys,xs=np.where(m); a=a[ys.min():ys.max()+1, xs.min():xs.max()+1]
    im=Image.fromarray(a).resize((40,40),Image.BILINEAR)
    b=np.asarray(im)<np.asarray(im).mean()
    d=np.asarray(Image.fromarray(a).resize((41,40),Image.BILINEAR)).astype(int)
    dh=(d[:,1:]>d[:,:-1])
    return np.concatenate([b.ravel(),dh.ravel()]).astype(np.uint8), (a.shape[1]/a.shape[0])
H={}
for r in inv:
    q=getq(r['tag'],r['qno'])
    if q is None: continue
    try:
        h=hashq(q)
    except Exception as e:
        h=None
    if h is not None: H[f"{r['tag']}-{r['qno']}"]=h
keys=list(H)
M=np.stack([H[k][0] for k in keys]); AR=np.array([H[k][1] for k in keys])
print(len(keys))
np.save('hashM.npy',M); json.dump({'keys':keys,'ar':AR.tolist()},open('hashK.json','w'))
