"""GK2020D-78: for each polygon find its symmetry axis and whether the axis leaves the outline through an edge (perpendicular) or through a vertex"""
from panels import *
import math
a=load('as/GK2020D-78.png'); bx=boxes(a,hlen=100,minw=80,minh=80)
show(a,bx)
def analyse(box):
    sub=np.pad(crop(a,box,1),6,constant_values=255); m=sub<128
    S=nd.binary_fill_holes(m)
    ys,xs=np.where(S); cx,cy=xs.mean(),ys.mean()
    H,W=S.shape
    best=None
    P=np.stack([xs-cx,ys-cy],1)
    for deg in np.arange(0,180,0.5):
        t=math.radians(deg); d=np.array([math.cos(t),math.sin(t)])   # axis direction (image coords)
        # reflect points about line through centroid with direction d
        proj=P@d; perp=P-np.outer(proj,d); R=np.outer(proj,d)-perp
        rx=np.rint(R[:,0]+cx).astype(int); ry=np.rint(R[:,1]+cy).astype(int)
        ok=(rx>=0)&(rx<W)&(ry>=0)&(ry<H)
        hit=S[ry[ok],rx[ok]].sum()
        score=hit/len(P)
        if best is None or score>best[0]: best=(score,deg)
    score,deg=best; t=math.radians(deg); d=np.array([math.cos(t),math.sin(t)]); n=np.array([-d[1],d[0]])
    # boundary pixels
    B=S&~nd.binary_erosion(S); by,bxs=np.where(B); Q=np.stack([bxs-cx,by-cy],1)
    along=Q@d; off=Q@n
    res=[]
    for sign in (1,-1):
        # outermost crossing of the axis in direction sign*d
        near=np.abs(off)<1.5
        sel=along[near]*sign
        tmax=sel.max()
        # all crossings (cluster along values)
        cr=np.sort(np.unique(np.round(sel[sel>0])))
        ncross=1+int((np.diff(cr)>4).sum()) if len(cr) else 0
        # local shape near the outermost crossing: boundary points with |off| in [4,14] and along within 25 of tmax
        loc=(np.abs(off)>=4)&(np.abs(off)<=14)&(np.abs(along*sign-tmax)<22)
        if loc.sum()<6: res.append((ncross,'?',None)); continue
        dev=np.abs(along[loc]*sign-tmax); slope=np.polyfit(np.abs(off[loc]),dev,1)[0]
        res.append((ncross,'边(垂直)' if abs(slope)<0.2 else '顶点',round(float(slope),2)))
    return score,deg,res
k=0
for band in bx:
    for b in band:
        k+=1; s,deg,res=analyse(b)
        print(f'图{k}: 对称度 {s:.3f} 轴方向 {deg}° (0=横,90=竖) 两端: {res}')
