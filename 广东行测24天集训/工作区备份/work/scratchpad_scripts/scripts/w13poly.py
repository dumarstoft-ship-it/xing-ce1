import numpy as np
from PIL import Image
im=Image.open('/home/user/work/out/PD-A/assets/GK2022D-73.png').convert('L')
A=np.array(im).astype(float)
panels={'Q1':(24,212,80,269),'Q2':(215,404,80,269),'Q3':(407,598,80,269),'Q4':(680,871,80,269),'Q5':(874,1063,80,269),
        'A':(255,447,301,491),'B':(449,638,301,491),'C':(641,830,301,491),'D':(832,1023,301,491)}
def boundary(mask):
    # Moore neighbor tracing of the largest blob outer boundary
    H,W=mask.shape
    ys,xs=np.nonzero(mask)
    start=(ys.min(), xs[ys==ys.min()].min())
    dirs=[(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1)]
    b=[start]; cur=start; prev_dir=6
    for _ in range(20000):
        found=False
        for k in range(8):
            d=(prev_dir+k)%8
            ny,nx=cur[0]+dirs[d][0],cur[1]+dirs[d][1]
            if 0<=ny<H and 0<=nx<W and mask[ny,nx]:
                cur=(ny,nx); b.append(cur); prev_dir=(d+5)%8; found=True; break
        if not found or (cur==start and len(b)>3): break
    return np.array([(x,y) for y,x in b],float)
def rdp(P,eps):
    if len(P)<3: return P
    a,b=P[0],P[-1]; ab=b-a; L=np.hypot(*ab)
    if L==0: d=np.hypot(*(P-a).T)
    else: d=np.abs(ab[0]*(P[:,1]-a[1])-ab[1]*(P[:,0]-a[0]))/L
    i=np.argmax(d)
    if d[i]>eps:
        return np.vstack([rdp(P[:i+1],eps)[:-1],rdp(P[i:],eps)])
    return np.vstack([a,b])
def poly(name,eps=2.2):
    x0,x1,y0,y1=panels[name]
    P=A[y0+4:y1-3, x0+4:x1-3]
    mask=P<128
    B=boundary(mask)
    # closed polygon simplification: split at farthest point
    i0=0; d=np.hypot(*(B-B[0]).T); i1=int(np.argmax(d))
    V=np.vstack([rdp(B[i0:i1+1],eps)[:-1], rdp(np.vstack([B[i1:],B[:1]]),eps)[:-1]])
    # remove near-duplicate / collinear vertices
    changed=True
    while changed and len(V)>3:
        changed=False
        n=len(V)
        for k in range(n):
            p,q,r=V[k-1],V[k],V[(k+1)%n]
            v1=p-q; v2=r-q
            ang=np.degrees(np.arccos(np.clip(v1@v2/np.hypot(*v1)/np.hypot(*v2),-1,1)))
            if ang>168 or np.hypot(*v1)<3:
                V=np.delete(V,k,0); changed=True; break
    # signed area to determine orientation
    x,y=V[:,0],V[:,1]; area=0.5*np.sum(x*np.roll(y,-1)-np.roll(x,-1)*y)
    out=[]
    n=len(V)
    for k in range(n):
        p,q,r=V[k-1],V[k],V[(k+1)%n]
        v1=p-q; v2=r-q
        ang=np.degrees(np.arccos(np.clip(v1@v2/np.hypot(*v1)/np.hypot(*v2),-1,1)))
        cross=(q-p)[0]*(r-q)[1]-(q-p)[1]*(r-q)[0]
        convex = (cross>0) == (area>0)
        interior= ang if convex else 360-ang
        out.append((tuple(np.round(q,1)),round(interior,1)))
    return out
