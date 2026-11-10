import numpy as np, itertools
def fold_all(cells):
    cells=set(cells); start=next(iter(sorted(cells)))
    frames={start:(np.array([0,0,0]),np.array([1,0,0]),np.array([0,0,1]),np.array([0,-1,0]))}; st=[start]
    while st:
        s=st.pop(); o,eu,ev,n=frames[s]
        for d,(dc,dr) in {'R':(1,0),'L':(-1,0),'U':(0,1),'D':(0,-1)}.items():
            t=(s[0]+dc,s[1]+dr)
            if t not in cells or t in frames: continue
            frames[t]={'R':(o+eu,-n,ev,eu),'L':(o-n,n,ev,-eu),'U':(o+ev,eu,-n,ev),'D':(o-n,eu,n,-ev)}[d]; st.append(t)
    if len(frames)!=len(cells): return None
    return [tuple(frames[c][3]) for c in cells]
def connected(cells):
    cells=set(cells); s=next(iter(cells)); seen={s}; st=[s]
    while st:
        a=st.pop()
        for d in ((1,0),(-1,0),(0,1),(0,-1)):
            b=(a[0]+d[0],a[1]+d[1])
            if b in cells and b not in seen: seen.add(b); st.append(b)
    return len(seen)==len(cells)
def ok(cells):
    res=[]
    # overlap: fold all (spanning-tree dependent! try all spanning trees is complex; BFS tree from different starts)
    for sub in itertools.combinations(cells,6):
        if connected(sub):
            f=fold_all(sub)
            if f and len(set(f))==6: res.append(('cut',sorted(set(cells)-set(sub))))
    return res
# grids (col,row) with row 0 = top for readability -> convert to row up = -row
def g(rows):
    cells=[]
    for r,line in enumerate(rows):
        for c,ch in enumerate(line):
            if ch=='#': cells.append((c,-r))
    return cells
opts={'A':g(['##..','.##.','..##']) , 'B':g(['..#.','####','..##']), 'C':g(['#...','#...','####']), 'D':g(['.#..','##..','####'])}
for k,v in opts.items(): print(k,len(v),ok(v)[:3])
