"""symq.py IMG [names...] : for each framed panel print, for each candidate symmetry (V=竖轴, H=横轴, D='\\'轴, A='/'轴, R180, R90),
the size (px) of the largest unmatched blob after a 3px tolerance; small (<~25 at 250dpi) means the symmetry holds. Also faces/parts.
Use '-' as a name to skip a panel (e.g. the gap between two groups)."""
import sys
from panels import *
def sqpad(m):
    h,w=m.shape; k=max(h,w)+8; out=np.zeros((k,k),bool)
    y=(k-h)//2; x=(k-w)//2; out[y:y+h,x:x+w]=m; return out
def unmatched(m1,m2,tol=3):
    b=nd.binary_dilation(m2,iterations=tol); a=nd.binary_dilation(m1,iterations=tol)
    u=(m1&~b)|(m2&~a)
    lab,n=nd.label(u,structure=np.ones((3,3)))
    return int(max(nd.sum(u,lab,range(1,n+1)))) if n else 0
def best_shift(q,f,rng=3):
    best=None
    for dy in range(-rng,rng+1):
        for dx in range(-rng,rng+1):
            t=np.roll(np.roll(f,dy,0),dx,1); u=unmatched(q,t)
            if best is None or u<best: best=u
    return best
def symfull(m):
    q=sqpad(m)
    T=dict(V=q[:,::-1],H=q[::-1,:],D=q.T,A=q[::-1,::-1].T,R180=q[::-1,::-1],R90=np.rot90(q))
    return {k:best_shift(q,v) for k,v in T.items()}
def report(img,names=()):
    a=load(img); bx=boxes(a); k=0; out={}
    for band in bx:
        for b in band:
            sub=crop(a,b,8); m=content(sub,pad=0)
            nm=names[k] if k<len(names) else f'p{k}'; k+=1
            if nm=='-' : continue
            if m.sum()<30: print(nm,'(empty)'); continue
            s=symfull(m); out[nm]=s
            axes=[x for x,v in s.items() if v<=25]
            print(f'{nm:5s}',s,'=> sym:',axes or 'none','| faces',regions(sub),'parts',parts(sub),'| dark px',int(m.sum()))
    return out
if __name__=='__main__':
    report(sys.argv[1],sys.argv[2:])
