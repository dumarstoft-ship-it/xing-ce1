"""Q50 exhaustive assembly check (standalone; reads q50_hidden.json produced by q50_hidden.py).

Pieces (x right, d back, z up; transcribed from 352.png, verified by re-rendering in q50_fit.py):
  P1 (11 cubes): visible 10 + (1,1,0) which is unobservable but REQUIRED (else (1,1,1) is disconnected).
  P2 (3 cubes): L-tromino, no unobservable cell inside its bounding box.
  Options: visible cubes + 'unobservable' cells (presence cannot be read from the drawing).

Mode 'bbox'  : hidden cells restricted to the option's own bounding box (natural reading), every subset tried.
Mode 'broad' : any subset of ALL unobservable cells found in the search region (incl. far-behind / below cells),
               tested by reverse matching: for every cuboid and every placement of P1, P2, the remainder R must
               be connected and some rotation+translation of R must contain all visible cubes and otherwise lie
               inside the unobservable set.
Rotations: the 24 proper rotations (pieces are rigid; mirror images not allowed)."""
import json, itertools, sys
import os
D=os.path.dirname(os.path.abspath(__file__))+'/'
HJ=json.load(open(D+'q50_hidden.json'))
tup=lambda L:{tuple(c) for c in L}
P1=tup(HJ['P1']['visible_cubes'])|{(1,1,0)}
P2=tup(HJ['P2']['visible_cubes'])
OPT={o:(tup(HJ[o]['visible_cubes']),tup(HJ[o]['unobservable_cells'])) for o in 'ABCD'}

def rotations():
    import numpy as np
    mats=[]
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1,-1),repeat=3):
            M=[[0]*3 for _ in range(3)]
            for i in range(3): M[i][perm[i]]=signs[i]
            det=(M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1])-M[0][1]*(M[1][0]*M[2][2]-M[1][2]*M[2][0])+M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0]))
            if det==1: mats.append(M)
    return mats
ROT=rotations(); assert len(ROT)==24
def apply(M,c): return tuple(sum(M[i][j]*c[j] for j in range(3)) for i in range(3))
def norm(s):
    m=[min(c[i] for c in s) for i in range(3)]
    return frozenset(tuple(c[i]-m[i] for i in range(3)) for c in s)
def orients(s): return {norm({apply(M,c) for c in s}) for M in ROT}
def dims(s): return tuple(max(c[i] for c in s)+1 for i in range(3))
def connected(s):
    s=set(s); 
    if not s: return False
    st=[next(iter(s))]; seen={st[0]}
    while st:
        c=st.pop()
        for d in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
            n=(c[0]+d[0],c[1]+d[1],c[2]+d[2])
            if n in s and n not in seen: seen.add(n); st.append(n)
    return len(seen)==len(s)
P1o=orients(P1); P2o=orients(P2)
def placements(orset, box):
    a,b,c=box
    for o in orset:
        dx,dy,dz=dims(o)
        for tx in range(a-dx+1):
            for ty in range(b-dy+1):
                for tz in range(c-dz+1):
                    yield frozenset((x+tx,y+ty,z+tz) for x,y,z in o)
def remainders(box):
    full=frozenset(itertools.product(range(box[0]),range(box[1]),range(box[2])))
    seen=set()
    for p1 in placements(P1o,box):
        rest=full-p1
        for p2 in placements(P2o,box):
            if p2<=rest:
                R=rest-p2
                key=norm(R) if R else None
                if R and key not in seen:
                    seen.add(key); yield R,p1,p2
def cuboids(vmin,vmax,maxd=10):
    p1d=sorted(dims(P1))
    for a in range(1,maxd+1):
        for b in range(a,maxd+1):
            for c in range(b,maxd+1):
                if vmin<=a*b*c<=vmax and all(x>=y for x,y in zip((a,b,c),p1d)): yield (a,b,c)
mode=sys.argv[1] if len(sys.argv)>1 else 'bbox'
print(f'P1: {len(P1)} cubes, dims {dims(P1)}; P2: {len(P2)} cubes; mode={mode}')
for o,(vis,unobs) in OPT.items():
    if mode=='bbox':
        bx=dims(norm(vis)); mn=[min(c[i] for c in vis) for i in range(3)]
        inbox=sorted(c for c in unobs if all(mn[i]<=c[i]<mn[i]+bx[i] for i in range(3)))
        results=[]
        for k in range(len(inbox)+1):
            for H in itertools.combinations(inbox,k):
                shape=vis|set(H)
                if not connected(shape):
                    results.append((H,len(shape),'disconnected')); continue
                target=orients(shape); V=14+len(shape); ok=[]
                for box in cuboids(V,V):
                    for R,p1,p2 in remainders(box):
                        if norm(R) in target: ok.append((box,sorted(p1),sorted(p2),sorted(R)))
                results.append((H,len(shape),ok))
        print(f'\nOption {o}: visible {len(vis)} cubes; unobservable cells inside its bounding box: {inbox}')
        for H,n,ok in results:
            if ok=='disconnected': print(f'   hidden filled {list(H)} -> {n} cubes: piece disconnected (invalid)')
            elif ok: print(f'   hidden filled {list(H)} -> {n} cubes: FITS, cuboid {ok[0][0]}, {len(ok)} distinct remainder(s); P1 at {ok[0][1]}, P2 at {ok[0][2]}, option occupies {ok[0][3]}')
            else: print(f'   hidden filled {list(H)} -> {n} cubes: no cuboid possible')
    else:
        vmin=14+len(vis); vmax=14+len(vis)+len(unobs); found=[]
        for box in cuboids(vmin,vmax):
            for R,p1,p2 in remainders(box):
                if len(R)<len(vis) or len(R)>len(vis)+len(unobs) or not connected(R): continue
                for M in ROT:
                    Rr=[apply(M,c) for c in R]
                    # translation must map some cell of Rr onto a fixed visible cube
                    v0=min(vis)
                    for c in Rr:
                        t=(v0[0]-c[0],v0[1]-c[1],v0[2]-c[2])
                        T={(x+t[0],y+t[1],z+t[2]) for x,y,z in Rr}
                        if vis<=T and (T-vis)<=unobs:
                            found.append((box,len(R),sorted(T-vis))); break
                    else: continue
                    break
        print(f'\nOption {o} (broad): visible {len(vis)}, unobservable {len(unobs)}; cuboid volumes {vmin}..{vmax}')
        if found:
            for f in found[:10]: print('   FITS: cuboid',f[0],'option cubes',f[1],'needs hidden cells',f[2])
            print('   total distinct fits:',len(found))
        else: print('   no assembly possible under any hidden-cell assignment')
