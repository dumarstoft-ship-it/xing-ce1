import numpy as np, itertools
from cube import rots
def fold(sq):
    start=next(iter(sq))
    frames={start:(np.array([0,0,0]),np.array([1,0,0]),np.array([0,0,1]),np.array([0,-1,0]))}; st=[start]
    while st:
        s=st.pop(); o,eu,ev,n=frames[s]
        for d,(dc,dr) in {'R':(1,0),'L':(-1,0),'U':(0,1),'D':(0,-1)}.items():
            t=(s[0]+dc,s[1]+dr)
            if t not in sq or t in frames: continue
            frames[t]={'R':(o+eu,-n,ev,eu),'L':(o-n,n,ev,-eu),'U':(o+ev,eu,-n,ev),'D':(o-n,eu,n,-ev)}[d]; st.append(t)
    assert len(frames)==6
    out=set()
    for s,(o,eu,ev,n) in frames.items():
        lt=sq[s]
        if lt is None: out.add((tuple(n),None,None))
        else:
            L,(dx,dy)=lt; v=dx*eu+dy*ev; out.add((tuple(n),L,tuple(v)))
    assert len({x[0] for x in out})==6
    return out
UP,DN,LF,RT=(0,1),(0,-1),(-1,0),(1,0)
def net(cells):  # cells: (col,rowTop)->spec ; convert row to up-positive
    return {(c,-r):v for (c,r),v in cells.items()}
N={
 'A':net({(2,0):None,(3,0):('C',UP),(0,1):('A',UP),(1,1):('C',RT),(2,1):('A',UP),(1,2):None}),
 'B':net({(0,0):('A',LF),(1,0):None,(2,0):('A',RT),(2,1):('C',DN),(3,1):None,(4,1):('C',UP)}),
 'C':net({(0,0):('C',LF),(1,0):('A',DN),(1,1):None,(2,1):('C',UP),(3,1):None,(1,2):('A',UP)}),
 'D':net({(1,0):('A',UP),(0,1):('C',DN),(1,1):None,(2,1):('C',DN),(3,1):None,(3,2):('A',UP)}),
}
cubes={k:fold(v) for k,v in N.items()}
def same(c1,c2):
    for M in rots():
        r={(tuple(M@np.array(n)),L,(tuple(M@np.array(v)) if v is not None else None)) for n,L,v in c1}
        if r==c2: return True
    return False
for a,b in itertools.combinations('ABCD',2): print(a,b,same(cubes[a],cubes[b]))
