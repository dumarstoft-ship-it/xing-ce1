"""Panel utilities: find framed boxes in a rendered question image; symmetry / topology measurements.
usage as module:  from panels import *"""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as nd
sys.path.insert(0,'/home/user/work/out2/PD2A/tools')
import grid as G
def load(f): return np.asarray(Image.open(f).convert('L')).astype(float)
def boxes(a, hlen=None, minw=60, minh=60, thr=150):
    """returns list of bands; each band list of (x0,y0,x1,y1) interior boxes left->right"""
    if hlen is None: hlen=int(a.shape[1]*0.12)
    return G.find_boxes(a, hlen=hlen, minw=minw, minh=minh, thr=thr)
def crop(a, box, margin=5):
    x0,y0,x1,y1=box; return a[y0+margin:y1-margin, x0+margin:x1-margin]
def content(sub, thr=150, pad=2):
    m=sub<thr; ys,xs=np.where(m)
    if not len(ys): return m
    return m[max(0,ys.min()-pad):ys.max()+1+pad, max(0,xs.min()-pad):xs.max()+1+pad]
def iou(m1,m2,dil=2):
    a=nd.binary_dilation(m1,iterations=dil); b=nd.binary_dilation(m2,iterations=dil)
    # tolerance: fraction of m1 pixels covered by dilated m2 and vice versa
    c1=(m1&b).sum()/max(1,m1.sum()); c2=(m2&a).sum()/max(1,m2.sum())
    return min(c1,c2)
def sym(m, dil=2):
    """symmetry scores of binary mask (tight content crop): dict of vertical-axis, horizontal-axis, diag, anti, rot180, rot90"""
    out={}
    out['V']=iou(m, m[:,::-1],dil)   # mirror about vertical axis
    out['H']=iou(m, m[::-1,:],dil)
    out['R180']=iou(m, m[::-1,::-1],dil)
    if abs(m.shape[0]-m.shape[1])<=6:
        k=min(m.shape); q=m[:k,:k]
        out['D']=iou(q,q.T,dil); out['A']=iou(q,q[::-1,::-1].T,dil); out['R90']=iou(q,np.rot90(q),dil)
    return {k:round(float(v),2) for k,v in out.items()}
def regions(sub, thr=150, minarea=12):
    """number of enclosed white regions (faces) in a panel crop: label white comps not touching border"""
    m=sub<thr
    w=~m
    lab,n=nd.label(w)   # 4-connectivity
    border=set(lab[0,:])|set(lab[-1,:])|set(lab[:,0])|set(lab[:,-1])
    areas=nd.sum(w,lab,range(1,n+1))
    return sum(1 for i in range(1,n+1) if i not in border and areas[i-1]>=minarea)
def parts(sub, thr=150, minarea=6):
    """number of connected dark components (8-connectivity)"""
    m=sub<thr
    lab,n=nd.label(m,structure=np.ones((3,3)))
    areas=nd.sum(m,lab,range(1,n+1))
    return sum(1 for a in areas if a>=minarea)
def show(a, bx, names=None):
    for bi,band in enumerate(bx):
        print('band',bi,[(b[0],b[1],b[2],b[3]) for b in band])

def _clusters(idx, gap=2):
    out=[]
    for i in idx:
        if out and i-out[-1][-1]<=gap: out[-1].append(i)
        else: out.append([i])
    return [(c[0],c[-1]) for c in out]
def boxes2(a, thr=150, minsize=70, frac=0.92):
    """robust frame finder: connected dark components whose bbox border is (almost) fully dark; split into cells by full-span inner lines.
    returns list of rows (top->bottom), each a list of interior boxes (x0,y0,x1,y1) left->right"""
    m=a<thr
    lab,n=nd.label(m,structure=np.ones((3,3)))
    sl=nd.find_objects(lab); cells=[]
    for i,s in enumerate(sl,1):
        if s is None: continue
        h=s[0].stop-s[0].start; w=s[1].stop-s[1].start
        if h<minsize or w<minsize: continue
        comp=(lab[s]==i)
        if comp[:3].any(0).mean()<frac or comp[-3:].any(0).mean()<frac or comp[:,:3].any(1).mean()<frac or comp[:,-3:].any(1).mean()<frac: continue
        vl=_clusters(np.where(comp.mean(0)>=frac)[0]); hl=_clusters(np.where(comp.mean(1)>=frac)[0])
        for (t0,t1),(b0,b1) in zip(hl,hl[1:]):
            for (l0,l1),(r0,r1) in zip(vl,vl[1:]):
                if b0-t1>=minsize*0.6 and r0-l1>=minsize*0.6:
                    cells.append((s[1].start+l1+1, s[0].start+t1+1, s[1].start+r0, s[0].start+b0))
    cells=sorted(set(cells),key=lambda c:(c[1],c[0])); rows=[]
    for c in cells:
        if rows and abs(c[1]-rows[-1][0][1])<25: rows[-1].append(c)
        else: rows.append([c])
    return [sorted(r) for r in rows]

def panels_of(a, thr=150, keep=0.55):
    """frames only (drop rectangles that belong to figures): keep boxes with area >= keep * max area"""
    rows=boxes2(a,thr); allb=[c for r in rows for c in r]
    if not allb: return []
    A=max((c[2]-c[0])*(c[3]-c[1]) for c in allb)
    out=[]
    for r in rows:
        rr=[c for c in r if (c[2]-c[0])*(c[3]-c[1])>=keep*A]
        if rr: out.append(rr)
    # merge rows that overlap vertically
    merged=[]
    for r in out:
        if merged and abs(r[0][1]-merged[-1][0][1])<25: merged[-1]=sorted(merged[-1]+r)
        else: merged.append(r)
    return merged
