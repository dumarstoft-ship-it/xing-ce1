"""split an unframed row of figures (classification questions) into separate figures by x-gaps; face adjacency etc."""
import numpy as np
from PIL import Image
from scipy import ndimage as nd
def load(f): return np.asarray(Image.open(f).convert('L')).astype(int)
def bands(m, mingap=12):
    rows=m.sum(1); ys=np.where(rows>0)[0]; segs=[];s=ys[0];p=ys[0]
    for y in ys[1:]:
        if y-p>mingap: segs.append((s,p)); s=y
        p=y
    segs.append((s,p)); return segs
def split_x(sub, mingap=25, minw=30):
    cols=sub.sum(0); xs=np.where(cols>0)[0]; segs=[];s=xs[0];p=xs[0]
    for x in xs[1:]:
        if x-p>mingap: segs.append((s,p)); s=x
        p=x
    segs.append((s,p)); return [g for g in segs if g[1]-g[0]>=minw]
def faces(fig, minarea=40):
    """fig: bool dark mask (padded). returns list of face masks (enclosed white regions)"""
    w=~fig; lab,n=nd.label(w)
    border=set(lab[0,:])|set(lab[-1,:])|set(lab[:,0])|set(lab[:,-1])
    return [lab==i for i in range(1,n+1) if i not in border and (lab==i).sum()>=minarea]
def adjacent_pairs(F, gap=6, minshare=8):
    """pairs of faces separated only by a thin line: dilate both by gap, overlap of dilations (excluding either face) large"""
    out=[]
    D=[nd.binary_dilation(f,iterations=gap) for f in F]
    for i in range(len(F)):
        for j in range(i+1,len(F)):
            ov=(D[i]&D[j]).sum()
            if ov>=minshare*gap: out.append((i,j,int(ov)))
    return out
def pad(m,k=10):
    return np.pad(m,k,constant_values=False)
