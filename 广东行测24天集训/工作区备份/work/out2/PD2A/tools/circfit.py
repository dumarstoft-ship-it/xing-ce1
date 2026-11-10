import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import ndimage as nd
from grid import *
def filled(region_dark):
    f=nd.binary_fill_holes(nd.binary_closing(region_dark,iterations=2))
    lab,n=nd.label(f)
    if n>1:
        sizes=nd.sum(f,lab,range(1,n+1)); f=lab==(1+int(np.argmax(sizes)))
    return f
def boundary_pts(f):
    e=f & ~nd.binary_erosion(f)
    ys,xs=np.where(e); return np.stack([xs,ys],1).astype(float)
def fit_circle(P):
    x,y=P[:,0],P[:,1]
    A=np.stack([x,y,np.ones_like(x)],1); b=x*x+y*y
    c=np.linalg.lstsq(A,b,rcond=None)[0]
    cx,cy=c[0]/2,c[1]/2; r=np.sqrt(c[2]+cx*cx+cy*cy); return cx,cy,r
def robust_circle(P, iters=8, keep=0.6):
    Q=P
    for _ in range(iters):
        cx,cy,r=fit_circle(Q)
        d=np.abs(np.hypot(P[:,0]-cx,P[:,1]-cy)-r)
        thr=np.quantile(d,keep)
        Q=P[d<=max(thr,1.5)]
    return fit_circle(Q)
def circle3(p1,p2,p3):
    ax,ay=p1; bx,by=p2; cx,cy=p3
    d=2*(ax*(by-cy)+bx*(cy-ay)+cx*(ay-by))
    if abs(d)<1e-6: return None
    ux=((ax*ax+ay*ay)*(by-cy)+(bx*bx+by*by)*(cy-ay)+(cx*cx+cy*cy)*(ay-by))/d
    uy=((ax*ax+ay*ay)*(cx-bx)+(bx*bx+by*by)*(ax-cx)+(cx*cx+cy*cy)*(bx-ax))/d
    return ux,uy,np.hypot(ax-ux,ay-uy)
def ransac_circle(P, n=4000, tol=2.0, seed=0):
    rng=np.random.default_rng(seed); best=None; bi=-1
    for _ in range(n):
        i=rng.choice(len(P),3,replace=False)
        c=circle3(*P[i])
        if c is None or c[2]<30 or c[2]>2000: continue
        d=np.abs(np.hypot(P[:,0]-c[0],P[:,1]-c[1])-c[2])
        k=(d<tol).sum()
        if k>bi: bi=k; best=c
    d=np.abs(np.hypot(P[:,0]-best[0],P[:,1]-best[1])-best[2])
    return fit_circle(P[d<tol]), bi
