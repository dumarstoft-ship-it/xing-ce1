"""GK2021D-73: fit the circle of the arc in each panel (RANSAC) and measure the angular span of the arc"""
import sys, math
sys.path.insert(0,'/home/user/work/out2/PD2A/tools')
from panels import *
from circfit import ransac_circle
a=load('as/GK2021D-73.png'); bx=panels_of(a)
names=['f1','f2','f3','f4','f5','?','A','B','C','D']; k=0
for band in bx:
    for b in band:
        nm=names[k]; k+=1
        if nm=='?': continue
        sub=crop(a,b,6); m=sub<128
        # thin: use boundary of dark for point set
        ys,xs=np.where(m); P=np.stack([xs,ys],1).astype(float)
        if len(P)>4000: P=P[::2]
        try: (cx,cy,r),n=ransac_circle(P,n=6000,tol=1.6,seed=1)
        except Exception as e: print(nm,'no circle',e); continue
        # angular coverage
        cov=[]
        for deg in range(360):
            t=math.radians(deg); hit=False
            for rr in (r-2,r-1,r,r+1,r+2):
                x=int(round(cx+rr*math.cos(t))); y=int(round(cy-rr*math.sin(t)))
                if 0<=x<m.shape[1] and 0<=y<m.shape[0] and m[y,x]: hit=True
            cov.append(hit)
        cov=np.array(cov); total=int(cov.sum())
        # longest run (cyclic)
        c2=np.concatenate([cov,cov]); best=cur=0
        for v in c2:
            cur=cur+1 if v else 0; best=max(best,cur)
        best=min(best,360)
        print(f'{nm}: circle centre ({cx:.0f},{cy:.0f}) r={r:.0f} inliers={n}  arc span (longest run) {best}°  total covered {total}°')
