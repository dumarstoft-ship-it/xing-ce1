import numpy as np
from PIL import Image
def load(f):
    return np.asarray(Image.open(f).convert('L')).astype(float)
def clusters(idx, gap=3):
    out=[]
    for i in idx:
        if out and i-out[-1][-1]<=gap: out[-1].append(i)
        else: out.append([i])
    return [(c[0],c[-1]) for c in out]
def longest_run(v):
    best=cur=0
    for x in v:
        cur=cur+1 if x else 0
        if cur>best: best=cur
    return best
def find_boxes(a, hlen=300, vfrac=0.9, minw=40, minh=40, thr=150):
    d=a<thr; H,W=d.shape
    runs=np.array([longest_run(r) for r in d])
    hl=clusters(np.where(runs>hlen)[0])
    bands=[]
    for (t0,t1),(b0,b1) in zip(hl,hl[1:]):
        if b0-t1<minh: continue
        band=d[t1+1:b0]
        vr=np.array([longest_run(c) for c in band.T])
        vl=clusters(np.where(vr>vfrac*band.shape[0])[0])
        boxes=[(l1+1,t1+1,r0,b0) for (l0,l1),(r0,r1) in zip(vl,vl[1:]) if r0-l1>minw]
        if boxes: bands.append(boxes)
    return bands
def content_bbox(a, box, margin=6, thr=150):
    x0,y0,x1,y1=box
    sub=a[y0+margin:y1-margin, x0+margin:x1-margin]<thr
    ys,xs=np.where(sub)
    if not len(ys): return None
    return (x0+margin+xs.min(), y0+margin+ys.min(), x0+margin+xs.max(), y0+margin+ys.max())
def sample(a, pts, r=3):
    return np.array([a[int(round(y))-r:int(round(y))+r+1, int(round(x))-r:int(round(x))+r+1].mean() for (x,y) in pts])
def square_lattice(bb, nr, nc):
    x0,y0,x1,y1=bb; w=(x1-x0)/nc; h=(y1-y0)/nr
    return [(x0+(j+0.5)*w, y0+(i+0.5)*h) for i in range(nr) for j in range(nc)]
def hex_lattice(bb, rows=(3,4,5,4,3)):
    x0,y0,x1,y1=bb; n=max(rows); d=(x1-x0)/n; cx=(x0+x1)/2
    k=len(rows); pts=[]
    for i,m in enumerate(rows):
        y=y0+d/2+i*((y1-y0)-d)/(k-1)
        for j in range(m): pts.append((cx+(j-(m-1)/2)*d, y))
    return pts
def show(bits, nr, nc, on='●', off='○'):
    return '\n'.join(''.join(on if bits[i*nc+j] else off for j in range(nc)) for i in range(nr))
def hex_lattice_cols(bb, cols=(3,4,5,4,3)):
    x0,y0,x1,y1=bb; n=max(cols); d=(y1-y0)/n; cy=(y0+y1)/2
    k=len(cols); pts=[]
    for i,m in enumerate(cols):
        x=x0+d/2+i*((x1-x0)-d)/(k-1)
        for j in range(m): pts.append((x, cy+(j-(m-1)/2)*d))
    return pts
