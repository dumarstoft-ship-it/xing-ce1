import itertools
# solid in front-view coords (x right, y back, z up), depth y=0..2
solid=set()
solid |= {(0,0,0),(1,0,0)}
solid |= {(0,1,0),(1,1,0),(2,1,0),(0,1,1),(1,1,1),(2,1,1),(1,1,2),(1,1,3)}
solid |= {(x,2,0) for x in range(4)} | {(x,2,1) for x in range(4)} | {(1,2,2),(2,2,2),(3,2,2),(1,2,3)}
print('solid size',len(solid))
P1={(0,0,2),(1,0,2),(2,0,2),(2,0,1),(2,0,0)}
P2={(0,0,3),(0,0,2),(0,0,1),(0,1,3),(1,0,1),(1,0,0)}
P3={(0,0,0),(1,0,0),(2,0,0),(1,0,1),(2,0,1)}
opts={
 'A':{(0,0,0),(0,1,0),(1,1,0),(0,1,1)},
 'B':{(0,0,0),(0,1,0),(1,1,0),(0,1,1),(1,1,1)},
 'C':{(0,0,0),(0,1,0),(0,2,0),(1,2,0),(0,2,1)},
 'D':{(0,0,0),(0,1,0),(0,2,0),(1,2,0),(0,2,1),(1,2,1)},
}
def rots():
    mats=[]
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product([1,-1],repeat=3):
            M=[[0]*3 for _ in range(3)]
            for i in range(3): M[i][perm[i]]=signs[i]
            # determinant
            import numpy as np
            if round(np.linalg.det(np.array(M)))==1: mats.append(M)
    return mats
R=rots()
def orient(p,mirror=False):
    out=set()
    for M in R:
        q=[tuple(sum(M[i][j]*c[j] for j in range(3)) for i in range(3)) for c in p]
        if mirror: q=[(-a,b,c) for a,b,c in q]
        mn=[min(c[i] for c in q) for i in range(3)]
        out.add(frozenset(tuple(c[i]-mn[i] for i in range(3)) for c in q))
    return out
def placements(p,mirror=False):
    res=[]
    os=orient(p) | (orient(p,True) if mirror else set())
    for o in os:
        for anchor in solid:
            o0=min(o)
            sh=[(c[0]-o0[0]+anchor[0],c[1]-o0[1]+anchor[1],c[2]-o0[2]+anchor[2]) for c in o]
            s=frozenset(sh)
            if s<=solid: res.append(s)
    return list(set(res))
for mirror in (False,True):
  print('--- mirror allowed' if mirror else '--- rotations only')
  for k,v in opts.items():
    if len(P1)+len(P2)+len(P3)+len(v)!=len(solid):
        print(k,'size mismatch',len(v)); continue
    pl=[placements(P,mirror) for P in (P1,P2,P3,v)]
    sols=[]
    for a in pl[0]:
        for b in pl[1]:
            if a&b: continue
            ab=a|b
            for c in pl[2]:
                if ab&c: continue
                abc=ab|c
                for d in pl[3]:
                    if abc&d: continue
                    if len(abc|d)==len(solid): sols.append((a,b,c,d))
    print(k,'solutions',len(sols))
    for s in sols[:3]:
        print('  ',[sorted(x) for x in s])
