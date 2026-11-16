# Q49: exhaustive check - place pieces 1 and 2 (all 24 rotations, all translations,
# colour must match) into the reconstructed polyhedron; compare remainder with options.
import itertools, sys
sys.path.insert(0, __file__.rsplit('/',1)[0])
from q49_render import POLY, P1, P2, OPT

def rotations():
    mats=[]
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product([1,-1],repeat=3):
            M=[[0]*3 for _ in range(3)]
            for i in range(3): M[i][perm[i]]=signs[i]
            # determinant
            det=(M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1])
                -M[0][1]*(M[1][0]*M[2][2]-M[1][2]*M[2][0])
                +M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0]))
            if det==1: mats.append(M)
    return mats
ROT=rotations(); assert len(ROT)==24

def apply(M,p): return tuple(sum(M[i][j]*p[j] for j in range(3)) for i in range(3))

def normalize(cubes):
    mn=[min(p[i] for p in cubes) for i in range(3)]
    return frozenset(((p[0]-mn[0],p[1]-mn[1],p[2]-mn[2]),c) for p,c in cubes.items())

def all_orient(cubes):
    out=set()
    for M in ROT:
        out.add(normalize({apply(M,p):c for p,c in cubes.items()}))
    return out

def placements(piece, target):
    res=[]
    tset=set(target)
    for M in ROT:
        rp={apply(M,p):c for p,c in piece.items()}
        anchor=next(iter(rp))
        for t in tset:
            off=tuple(t[i]-anchor[i] for i in range(3))
            moved={tuple(p[i]+off[i] for i in range(3)):c for p,c in rp.items()}
            if all(q in target and target[q]==c for q,c in moved.items()):
                fs=frozenset(moved)
                if fs not in [frozenset(r) for r in res]: res.append(moved)
    return res

def connected(cells):
    cells=set(cells)
    if not cells: return True
    st=[next(iter(cells))]; seen=set(st)
    while st:
        x,y,z=st.pop()
        for d in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
            n=(x+d[0],y+d[1],z+d[2])
            if n in cells and n not in seen: seen.add(n); st.append(n)
    return len(seen)==len(cells)

optn={k:all_orient(v) for k,v in OPT.items()}
P2b=dict(P2); P2b[(0,1,0)]='w'   # variant: piece 2 with a fully hidden extra cube
for name2,piece2 in [('P2(6)',P2),('P2+hidden(7)',P2b)]:
    for a in placements(P1,POLY):
        for b in placements(piece2,POLY):
            if set(a)&set(b): continue
            rest={p:c for p,c in POLY.items() if p not in a and p not in b}
            if not connected(rest): continue
            n=normalize(rest)
            hits=[k for k,v in optn.items() if n in v]
            print(name2,'P1@',sorted(a),'P2@',sorted(b),'rest',len(rest),sorted(rest.items()),'->',hits)
