"""Fold a net of unit squares onto the surface of an X*Y*Z box (surface walk).
net: set of (row, col) unit cells (image: col -> right, row -> down).
Returns list of valid foldings: dict cell -> (center(3), n, u, v) with u = image-right, v = image-down in 3D.
World: x right, y up, z toward viewer (front)."""
import numpy as np, itertools
def surface_squares(X,Y,Z):
    out=[]
    dims=(X,Y,Z)
    for ax in range(3):
        for sgn in (-1,1):
            n=np.zeros(3,int); n[ax]=sgn
            o=[a for a in range(3) if a!=ax]
            for i in range(dims[o[0]]):
                for j in range(dims[o[1]]):
                    c=np.zeros(3); c[ax]=dims[ax] if sgn>0 else 0; c[o[0]]=i+0.5; c[o[1]]=j+0.5
                    out.append((tuple(c),tuple(n)))
    return out
def step(c,n,d,dims):
    c=np.array(c,float); n=np.array(n); d=np.array(d)
    p=c+d
    ax=int(np.nonzero(d)[0][0])
    if 0<p[ax]<dims[ax]:
        return p,n,None   # same face
    # over the edge
    p=c+d/2.0-n/2.0
    return p,d,-n
def rot_over(n,d):
    """rotation matrix mapping n->d, d->-n, fixing e=n x d"""
    e=np.cross(n,d)
    A=np.stack([n,d,e],1).astype(float); B=np.stack([d,-n,e],1).astype(float)
    return B@np.linalg.inv(A)
def fold(net,dims,start_cell=None):
    cells=sorted(net); start=start_cell or cells[0]
    sq=surface_squares(*dims); allsq=set((tuple(np.round(np.array(c),2)),n) for c,n in sq)
    results=[]
    for c0,n0 in sq:
        n0=np.array(n0)
        tang=[t for t in (np.eye(3,dtype=int).tolist()+(-np.eye(3,dtype=int)).tolist()) if np.dot(t,n0)==0]
        for u0 in tang:
            u0=np.array(u0); v0=np.cross(n0,u0)*-1  # choose v so that (u,v,n) right-handed as seen from outside: u x v = -n? check below
            # viewing face from outside (looking along -n): image right=u, image down=v -> u x (-v) should = n  (right x up = toward viewer)
            if not (np.cross(u0,-v0)==n0).all(): v0=-v0
            fr={start:(np.array(c0,float),n0,u0,v0)}; todo=[start]; ok=True
            while todo and ok:
                cell=todo.pop(); c,n,u,v=fr[cell]; r,k=cell
                for (dr,dk),d in (((0,1),u),((0,-1),-u),((1,0),v),((-1,0),-v)):
                    nb=(r+dr,k+dk)
                    if nb not in net: continue
                    p,n2,nd=step(c,n,d,dims)
                    if nd is None: u2,v2=u,v
                    else:
                        R=rot_over(n,d); u2=np.rint(R@u).astype(int); v2=np.rint(R@v).astype(int)
                    if nb in fr:
                        pc,pn,_,_=fr[nb]
                        if not (np.allclose(pc,p) and (pn==n2).all()): ok=False
                        continue
                    fr[nb]=(p,np.array(n2),u2,v2); todo.append(nb)
            if not ok or len(fr)!=len(net): continue
            keys=set((tuple(np.round(fr[k][0],2)),tuple(fr[k][1])) for k in fr)
            if len(keys)==len(net)==len(allsq) and keys==allsq: results.append(fr)
    return results
