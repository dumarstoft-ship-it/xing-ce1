import numpy as np
def refl(p, d):
    """reflection across line through p with direction d: returns 3x3 affine"""
    d=np.array(d,float); d/=np.linalg.norm(d)
    R=2*np.outer(d,d)-np.eye(2)
    A=np.eye(3); A[:2,:2]=R; A[:2,2]=np.array(p)-R@np.array(p)
    return A
def turns(creases):
    """creases: list of '/' or '\\' at positions 1..n along strip (strip runs +x, t up). returns list of turn signs (+1 left/ccw, -1 right/cw)"""
    T=np.eye(3); dirs=[]
    d0=T[:2,:2]@np.array([1.0,0]); dirs.append(d0)
    for i,o in enumerate(creases):
        s=i+1.0
        dl=np.array([1.0,1.0]) if o=='/' else np.array([1.0,-1.0])
        p=T@np.array([s,0,1.0]); dp=T[:2,:2]@dl
        T=refl(p[:2],dp)@T
        dirs.append(T[:2,:2]@np.array([1.0,0]))
    out=[]
    for a,b in zip(dirs,dirs[1:]):
        cr=a[0]*b[1]-a[1]*b[0]; out.append('L' if cr>0 else 'R')
    return ''.join(out)
if __name__=="__main__":
  opts={'A':'\\\\//','B':'\\//\\','C':'/\\/\\','D':'////'}
  for k,v in opts.items():
      t=turns(list(v)); rev=turns(list(v[::-1]))
      print(k, v, "turns", t, "reversed strip", rev)
