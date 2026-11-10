import numpy as np, itertools
from cube import rots
sq={(0,0):'G',(1,0):'W1',(1,1):'W2',(2,1):'W3',(3,1):'W4',(3,2):'K'}
start=(1,1)
frames={start:(np.array([0,0,0]),np.array([1,0,0]),np.array([0,0,1]),np.array([0,-1,0]))}
st=[start]
while st:
    s=st.pop(); o,eu,ev,n=frames[s]
    for d,(dc,dr) in {'R':(1,0),'L':(-1,0),'U':(0,1),'D':(0,-1)}.items():
        t=(s[0]+dc,s[1]+dr)
        if t not in sq or t in frames: continue
        fr={'R':(o+eu,-n,ev,eu),'L':(o-n,n,ev,-eu),'U':(o+ev,eu,-n,ev),'D':(o-n,eu,n,-ev)}[d]
        frames[t]=fr; st.append(t)
def P(s,a,b):
    o,eu,ev,n=frames[s]; return tuple(o+a*eu+b*ev)
normal={sq[s]:tuple(frames[s][3]) for s in sq}
print(normal)
edges={'1':(P((3,2),0,1),P((3,2),1,1)),'3':(P((3,2),0,0),P((3,2),1,0)),'4':(P((0,0),0,1),P((0,0),1,1)),'2':(P((0,0),0,0),P((0,0),1,0))}
print(edges)
# find rotation with K top (+z), G right (+x)
for M in rots():
    if tuple(M@np.array(normal['K']))==(0,0,1) and tuple(M@np.array(normal['G']))==(1,0,0):
        def rp(p): return tuple(int(v) for v in ((M@(np.array(p)*2-1))+1)//2)
        named={'D':frozenset([(0,1,1),(1,1,1)]),'C':frozenset([(0,0,1),(1,0,1)]),'B':frozenset([(1,0,0),(1,0,1)]),'A':frozenset([(1,1,0),(1,1,1)])}
        for k,(p,q) in edges.items():
            e=frozenset([rp(p),rp(q)])
            print(k,'->',[nm for nm,v in named.items() if v==e], sorted(e))
