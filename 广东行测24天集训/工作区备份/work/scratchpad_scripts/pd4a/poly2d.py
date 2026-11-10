"""polygon utilities without cv2: trace outer contour of a filled mask, simplify with RDP, count vertices / concave vertices"""
import numpy as np, math
from scipy import ndimage as nd
def trace(S):
    """Moore-neighbour boundary tracing of the largest component of boolean mask S; returns list of (x,y)"""
    lab,n=nd.label(S)
    if n>1:
        sizes=nd.sum(S,lab,range(1,n+1)); S=lab==(1+int(np.argmax(sizes)))
    S=np.pad(S,1)
    ys,xs=np.where(S); i=np.lexsort((xs,ys))[0]; start=(xs[i],ys[i])
    nb=[(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]  # clockwise in image coords starting east
    cur=start; prev_dir=6  # came from north
    out=[start]
    for _ in range(200000):
        found=False
        for k in range(8):
            d=(prev_dir+1+k)%8   # start searching from the direction after the backtrack
            x=cur[0]+nb[d][0]; y=cur[1]+nb[d][1]
            if S[y,x]:
                cur=(x,y); prev_dir=(d+4)%8; found=True; break
        if not found: break
        if cur==start and len(out)>2: break
        out.append(cur)
    return [(x-1,y-1) for x,y in out]
def rdp(pts, eps):
    pts=np.array(pts,float)
    def rec(a,b):
        if b<=a+1: return [a]
        p=pts[a]; q=pts[b]; d=q-p; L=np.hypot(*d)
        seg=pts[a+1:b]
        dist=np.abs((seg[:,0]-p[0])*d[1]-(seg[:,1]-p[1])*d[0])/L if L>0 else np.hypot(seg[:,0]-p[0],seg[:,1]-p[1])
        i=int(np.argmax(dist))
        if dist[i]>eps: return rec(a,a+1+i)+rec(a+1+i,b)
        return [a]
    # split closed contour at the farthest point from the start
    n=len(pts); far=int(np.argmax(np.hypot(pts[:,0]-pts[0,0],pts[:,1]-pts[0,1])))
    idx=rec(0,far)+rec(far,n-1)+[n-1]
    P=pts[idx]
    # merge near-duplicate & collinear vertices cyclically
    changed=True
    while changed and len(P)>3:
        changed=False; n=len(P)
        for i in range(n):
            a,b,c=P[i-1],P[i],P[(i+1)%n]
            if np.hypot(*(b-a))<eps*1.5:
                P=np.delete(P,i,0); changed=True; break
            v1=b-a; v2=c-b
            ang=abs(math.degrees(math.atan2(v1[0]*v2[1]-v1[1]*v2[0], v1@v2)))
            if ang<12:
                P=np.delete(P,i,0); changed=True; break
    return P
def turns(P):
    """signed turning angles; contour traced clockwise on screen -> convex vertices have positive cross in image coords"""
    n=len(P); out=[]
    for i in range(n):
        a,b,c=P[i-1],P[i],P[(i+1)%n]; v1=b-a; v2=c-b
        out.append(math.degrees(math.atan2(v1[0]*v2[1]-v1[1]*v2[0], v1@v2)))
    return out
