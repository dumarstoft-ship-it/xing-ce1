import itertools, numpy as np, json, sys
def rots():
    R=[]
    for p in itertools.permutations(range(3)):
        for s in itertools.product([1,-1],repeat=3):
            M=np.zeros((3,3),int)
            for i in range(3): M[i,p[i]]=s[i]
            if round(np.linalg.det(M))==1: R.append(M)
    return R
ROTS=rots()
def norm(cells):
    a=np.array(sorted(cells)); a=a-a.min(0); return tuple(sorted(map(tuple,a)))
def orientations(cells):
    out=set()
    for M in ROTS:
        out.add(norm([tuple(M@np.array(c)) for c in cells]))
    return out
def canon(cells): return min(orientations(cells))
def placements(cells,N=3):
    res=set()
    for o in orientations(cells):
        a=np.array(o); mx=a.max(0)
        if (mx>=N).any(): continue
        for t in itertools.product(*[range(N-m) for m in mx]):
            res.add(frozenset(tuple(c+np.array(t)) for c in a))
    return res
def connected(cells):
    cells=set(cells); s=next(iter(cells)); seen={s}; st=[s]
    while st:
        a=st.pop()
        for d in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
            b=(a[0]+d[0],a[1]+d[1],a[2]+d[2])
            if b in cells and b not in seen: seen.add(b); st.append(b)
    return len(seen)==len(cells)
FULL=frozenset(itertools.product(range(3),repeat=3))
G=[(0,0,2),(1,0,2),(1,1,2),(1,2,2),(1,2,1),(1,2,0)]
Ybase=[(0,0,0),(0,0,1),(0,0,2),(0,1,1),(0,1,2),(0,2,1),(1,0,0),(1,1,0),(1,2,0)]
hidden=[(0,1,0),(0,2,0)]
results={}
for k in range(3):
    for hs in itertools.combinations(hidden,k):
        Y=Ybase+list(hs)
        PY=placements(Y); PG=placements(G)
        comps=set()
        for py in PY:
            for pg in PG:
                if py & pg: continue
                R=FULL-py-pg
                if connected(R): comps.add(canon(R))
        results[str(hs)]=[[list(map(int,x)) for x in c] for c in comps]
        print('hidden',hs,'|Y|',len(Y),'placements',len(PY),len(PG),'distinct complements',len(comps),'sizes',sorted({len(c) for c in comps}))
json.dump(results,open('comps.json','w'))
