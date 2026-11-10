"""GK2018D-80: for each of six figures find triangle vertices, their angles, and which vertex the small circle sits on"""
import numpy as np, math, itertools
from PIL import Image
from scipy import ndimage as nd
from scipy.spatial import ConvexHull
a=np.asarray(Image.open('as/GK2018D-80.png').convert('L')).astype(int)
m=a<170
y0,y1=224,355
sub=m[y0-6:y1+7]
# enclosed white regions
w=~sub; lab,n=nd.label(w)
border=set(lab[0,:])|set(lab[-1,:])|set(lab[:,0])|set(lab[:,-1])
holes=[]
for i in range(1,n+1):
    if i in border: continue
    ys_,xs_=np.where(lab==i)
    if len(ys_)<60: continue
    holes.append((xs_.mean(),ys_.mean(),len(ys_),np.stack([xs_,ys_],1).astype(float)))
big=[h for h in holes if h[2]>1500]; small=[h for h in holes if h[2]<=1500]
big.sort(key=lambda h:h[0])
print('triangles',len(big),'circles',len(small),[(round(h[0]),round(h[1]),h[2]) for h in small])
def cross(u,v): return u[0]*v[1]-u[1]*v[0]
def tri_from_points(P):
    hull=P[ConvexHull(P).vertices]; best=None
    for i,j,k in itertools.combinations(range(len(hull)),3):
        A,B,C=hull[i],hull[j],hull[k]; ar=abs(cross(B-A,C-A))/2
        if best is None or ar>best[0]: best=(ar,(A,B,C))
    return best[1]
def angle(P,Q,R):
    v1=Q-P; v2=R-P; c=np.dot(v1,v2)/np.linalg.norm(v1)/np.linalg.norm(v2); return math.degrees(math.acos(max(-1,min(1,c))))
for k,h in enumerate(big,1):
    T=tri_from_points(h[3]); A,B,C=T
    angs=[angle(A,B,C),angle(B,A,C),angle(C,A,B)]
    # nearest small hole (circle)
    best=None
    for c in small:
        for j,V in enumerate(T):
            d=math.hypot(c[0]-V[0],c[1]-V[1])
            if best is None or d<best[0]: best=(d,j)
    j=best[1]; order=sorted(range(3),key=lambda i:angs[i])
    rank={order[0]:'最小角',order[1]:'中间角',order[2]:'最大角'}[j]
    print(f'图{k}: 三个内角',[round(x,1) for x in angs],'| 小圆所在顶点的角',round(angs[j],1),rank,'| 圆心到该顶点距离',round(best[0],1))
