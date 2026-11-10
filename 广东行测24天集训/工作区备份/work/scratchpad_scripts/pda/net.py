import numpy as np, itertools
from cube import rots
def fold(squares):
    """squares: dict (col,row)->marks ; row increases upward. marks: list of tuples like ('diag',(a,b),(c,d)) local corners.
    returns dict face_normal(tuple)->list of 3D marks (frozenset of corner pairs) ; raises if overlap"""
    start=next(iter(squares))
    frames={start:(np.array([0,0,0]),np.array([1,0,0]),np.array([0,0,1]),np.array([0,-1,0]))}
    stack=[start]
    while stack:
        s=stack.pop(); o,eu,ev,n=frames[s]
        for d,(dc,dr) in {'R':(1,0),'L':(-1,0),'U':(0,1),'D':(0,-1)}.items():
            t=(s[0]+dc,s[1]+dr)
            if t not in squares or t in frames: continue
            if d=='R': fr=(o+eu,-n,ev,eu)
            if d=='L': fr=(o-n,n,ev,-eu)
            if d=='U': fr=(o+ev,eu,-n,ev)
            if d=='D': fr=(o-n,eu,n,-ev)
            frames[t]=fr; stack.append(t)
    faces={}
    for s,(o,eu,ev,n) in frames.items():
        key=tuple(n)
        if key in faces: raise ValueError('overlap at %s'%(s,))
        ms=set()
        for m in squares[s]:
            if m[0]=='diag':
                p=tuple(o+m[1][0]*eu+m[1][1]*ev); q=tuple(o+m[2][0]*eu+m[2][1]*ev)
                ms.add(('diag',frozenset([p,q])))
            else: ms.add(m)
        faces[key]=ms
    if len(faces)!=6: raise ValueError('not 6 faces')
    return faces
def rot_faces(faces,M):
    out={}
    for n,ms in faces.items():
        n2=tuple(M@np.array(n)); ms2=set()
        for m in ms:
            if m[0]=='diag':
                ps=[tuple(int(v) for v in ((M@(np.array(p)*2-1))+1)//2) for p in m[1]]
                ms2.add(('diag',frozenset(ps)))
            else: ms2.add(m)
        out[n2]=ms2
    return out
def same(f1,f2):
    for M in rots():
        r=rot_faces(f1,M)
        if all(r[k]==f2.get(k,set()) for k in r): return True
    return False
