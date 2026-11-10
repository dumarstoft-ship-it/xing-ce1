import json, sys, itertools, numpy as np
from render import render
exec(open('asm.py').read().split('FULL=')[0])
res=json.load(open('comps.json'))
comps=[canon([tuple(x) for x in c]) for c in res["((0, 1, 0), (0, 2, 0))"]]
def img(cells): return np.array(render(list(cells),X0=300,Y0=700,W=1100,H=900).convert('L'))
def hidden_cands(V):
    base=img(V); out=[]
    for c in itertools.product(range(-2,4),range(-1,5),range(-1,4)):
        if c in V: continue
        if (img(set(V)|{c})!=base).sum()==0: out.append(c)
    return out
def check(name,V):
    V=set(map(tuple,V)); H=hidden_cands(V)
    need=10-len(V)
    print(name,'visible',len(V),'hidden candidates',len(H),'need extra',need)
    hits=[]
    if need<0: print('  too many cubes -> fail'); return
    for S in itertools.combinations(H,need):
        T=V|set(S)
        if not connected(T): continue
        cn=canon(T)
        if cn in comps: hits.append((comps.index(cn),S))
    print('  congruent completions:',hits[:5],'count',len(hits))
if __name__=='__main__':
    sets=json.loads(sys.argv[1])
    for k,v in sets.items(): check(k,[tuple(x) for x in v])
