"""Polycube toolkit. A polycube is a set of integer (x,y,z) tuples. x=right, y=back(depth), z=up."""
import itertools, numpy as np
def _rots():
    R=[]
    for p in itertools.permutations(range(3)):
        for s in itertools.product([1,-1],repeat=3):
            M=np.zeros((3,3),int)
            for i in range(3): M[i,p[i]]=s[i]
            if round(np.linalg.det(M))==1: R.append(M)
    return R
ROTS=_rots()
MIRROR=np.diag([-1,1,1])
def norm(P):
    P=np.array(sorted(P)); m=P.min(0); return tuple(sorted(map(tuple,P-m)))
def orientations(P, mirror=False):
    A=np.array(list(P))
    if mirror: A=A@MIRROR.T
    return {norm(map(tuple,A@R.T)) for R in ROTS}
def same(P,Q):
    """'rot' if Q is a rotation of P, 'mirror' if only a mirror image, None otherwise"""
    q=norm(Q)
    if q in orientations(P): return 'rot'
    if q in orientations(P,mirror=True): return 'mirror'
    return None
def views(P):
    A=np.array(list(P)); A=A-A.min(0)
    X,Y,Z=A.max(0)+1
    front=np.zeros((Z,X),int); top=np.zeros((Y,X),int); left=np.zeros((Z,Y),int)
    for x,y,z in A:
        front[Z-1-z,x]=1; top[Y-1-y,x]=1; left[Z-1-z,Y-1-y]=1   # left view: looking from -x toward +x, depth axis y reversed so back appears on left? see note
    return front,top,left
def show2(M):
    return '\n'.join(''.join('#' if v else '.' for v in row) for row in M)
def placements(piece, box):
    """all placements (frozensets) of piece (with rotations) inside box (set of cells)."""
    out=set()
    bx=np.array(list(box)); mn=bx.min(0); mx=bx.max(0)
    for o in orientations(piece):
        O=np.array(o); size=O.max(0)
        for dx in range(mn[0],mx[0]-size[0]+1):
            for dy in range(mn[1],mx[1]-size[1]+1):
                for dz in range(mn[2],mx[2]-size[2]+1):
                    cells=frozenset(map(tuple,O+[dx,dy,dz]))
                    if cells<=box: out.add(cells)
    return out
def exact_cover(target, pieces):
    """can pieces (list of polycubes) exactly tile target (set)? returns one solution list or None"""
    target=frozenset(target)
    if sum(len(p) for p in pieces)!=len(target): return None
    P=[placements(p,target) for p in pieces]
    order=sorted(range(len(pieces)),key=lambda i:len(P[i]))
    sol=[]
    def rec(k, rem):
        if k==len(order): return not rem
        i=order[k]
        for pl in P[i]:
            if pl<=rem:
                sol.append((i,pl))
                if rec(k+1, rem-pl): return True
                sol.pop()
        return False
    return sol if rec(0,target) else None
