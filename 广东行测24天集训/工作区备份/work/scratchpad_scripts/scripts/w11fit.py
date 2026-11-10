import numpy as np, sys, json
from PIL import Image
im=Image.open('/home/user/work/out/PD-A/assets/GK2018D-71.png').convert('L')
A=np.array(im).astype(float)
# panels: question row y 74..200 ; option row y 222..347
qx=[353,481,608,735,862,989]; ox=[481,608,735,862,990]
def panel(kind,i):
    if kind=='q': return A[75:200, qx[i]+3:qx[i+1]-1]
    return A[223:347, ox[i]+3:ox[i+1]-1]
def darkpts(P,thr=140):
    ys,xs=np.nonzero(P<thr); w=(255-P[ys,xs])/255.0
    return np.stack([xs,ys],1).astype(float), w
def fit_circle(pts,w,c0,r0,band=4,iters=6):
    c=np.array(c0,float); r=r0
    for _ in range(iters):
        d=np.hypot(pts[:,0]-c[0],pts[:,1]-c[1])
        m=np.abs(d-r)<band
        x,y=pts[m,0],pts[m,1]; ww=w[m]
        # algebraic fit x^2+y^2+Dx+Ey+F=0 weighted
        M=np.stack([x,y,np.ones_like(x)],1)*np.sqrt(ww)[:,None]
        b=-(x**2+y**2)*np.sqrt(ww)
        D,E,F=np.linalg.lstsq(M,b,rcond=None)[0]
        c=np.array([-D/2,-E/2]); r=np.sqrt(c[0]**2+c[1]**2-F)
    return c,r
def fit_line(pts,w,p,q,band=2.0,circle=None):
    p=np.array(p,float); q=np.array(q,float)
    for _ in range(5):
        d=q-p; L=np.linalg.norm(d); u=d/L; n=np.array([-u[1],u[0]])
        rel=pts-p; t=rel@u; s=rel@n
        m=(np.abs(s)<band)&(t>-1)&(t<L+1)
        if circle is not None:
            c,r=circle; dc=np.hypot(pts[:,0]-c[0],pts[:,1]-c[1]); m&=np.abs(dc-r)>2.2
        P=pts[m]; ww=w[m]
        mu=(P*ww[:,None]).sum(0)/ww.sum()
        C=((P-mu)*ww[:,None]).T@(P-mu)
        ev,evec=np.linalg.eigh(C); u2=evec[:,1]
        if u2@u<0: u2=-u2
        t2=(P-mu)@u2
        # endpoints: robust extremes
        p=mu+u2*np.percentile(t2,0.5); q=mu+u2*np.percentile(t2,99.5)
    return p,q
def inter(a,b):
    p1,q1=a; p2,q2=b
    d1=q1-p1; d2=q2-p2
    M=np.array([d1,-d2]).T
    if abs(np.linalg.det(M))<1e-9: return None
    t,s=np.linalg.solve(M,p2-p1)
    return p1+t*d1,t,s
