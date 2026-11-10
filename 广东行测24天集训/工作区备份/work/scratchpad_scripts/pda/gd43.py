from cube import *
# reference cube for GD2022X-43 net (c front y=0, b left x=0, d right x=1, e back y=1, a top z=1, f bottom z=0)
P={
 'F':dict(diag=((0,0,0),(1,0,1)), black=(1,0,0)),     # c: front, / from (x0,z0) to (x1,z1), black bottom-right corner
 'L':dict(diag=((0,1,1),(0,0,0)), black=(0,1,0)),     # b: left, from (y1,z1) to (y0,z0), black near (y1,z0)
 'R':dict(diag=((1,0,0),(1,1,1)), black=(1,0,1)),     # d: right, from (y0,z0) to (y1,z1), black near (y0,z1)
 'K':dict(diag=((1,1,1),(0,1,0)), black=None),        # e: back, from (x1,z1) to (x0,z0), white
 'U':dict(diag=((0,1,1),(1,0,1)), black=None),        # a: top, from (x0,y1) to (x1,y0), white
 'D':dict(diag=((0,1,0),(1,0,0)), black=(0,0,0)),     # f: bottom, from (x0,y1) to (x1,y0), black near (x0,y0)
}
seen=set()
for M in rots():
    d=describe(P,M)
    key=str(sorted((k,tuple(sorted(v.items()))) for k,v in d.items()))
    if key in seen: continue
    seen.add(key)
    print({k:d[k] for k in ('front','top','right')})
