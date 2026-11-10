import itertools
import numpy as np
# cube state: orientation as rotation matrix; the face touching the 'ground' is the face currently under the paper square.
# Rolling paper over a fixed cube: equivalently roll the cube over the paper. Track which cube face (as body-frame normal) is down.
def roll(R,d):
    # d in 'E','W','N','S' ; rotate cube about horizontal axis (grid: x right, y down; z up)
    if d=='E': M=np.array([[0,0,1],[0,1,0],[-1,0,0]])   # rotate about y axis
    if d=='W': M=np.array([[0,0,-1],[0,1,0],[1,0,0]])
    if d=='S': M=np.array([[1,0,0],[0,0,1],[0,-1,0]])  # about x axis
    if d=='N': M=np.array([[1,0,0],[0,0,-1],[0,1,0]])
    return M@R
def down_face(R):
    # body-frame normal currently pointing to world -z
    v=R.T@np.array([0,0,-1]); return tuple(int(round(t)) for t in v)
def fold(cells,edges):
    # edges: set of frozenset pairs used as folds (tree). returns dict cell->face, and consistency for cycles
    cells=list(cells); adj={c:[] for c in cells}
    for e in edges:
        a,b=tuple(e); adj[a].append(b); adj[b].append(a)
    root=cells[0]; R0=np.eye(3,dtype=int); state={root:R0}; stack=[root]
    while stack:
        c=stack.pop()
        for n in adj[c]:
            dx,dy=n[0]-c[0],n[1]-c[1]
            d={(1,0):'E',(-1,0):'W',(0,1):'S',(0,-1):'N'}[(dx,dy)]
            Rn=roll(state[c],d)
            if n in state:
                if not np.array_equal(state[n],Rn): return None   # inconsistent cycle (cannot fold w/o cutting)
            else:
                state[n]=Rn; stack.append(n)
    if len(state)!=len(cells): return None
    return {c:down_face(R) for c,R in state.items()}
def neighbors(cells):
    S=set(cells); E=[]
    for (x,y) in S:
        for (dx,dy) in [(1,0),(0,1)]:
            if (x+dx,y+dy) in S: E.append(frozenset([(x,y),(x+dx,y+dy)]))
    return E
def connected(cells,edges):
    cells=list(cells)
    if not cells: return False
    adj={c:[] for c in cells}
    for e in edges:
        a,b=tuple(e); adj[a].append(b); adj[b].append(a)
    seen={cells[0]}; st=[cells[0]]
    while st:
        c=st.pop()
        for n in adj[c]:
            if n not in seen: seen.add(n); st.append(n)
    return len(seen)==len(cells)
def analyze(cells):
    res={'net6_nocut':[], 'cover_nocut':[], 'cover_withslits':[]}
    cells=list(cells)
    for k in range(6,len(cells)+1):
        for sub in itertools.combinations(cells,k):
            E=neighbors(sub)
            if not connected(sub,E): continue
            f=fold(sub,E)
            if f is not None and len(set(f.values()))==6:
                (res['net6_nocut'] if k==6 else res['cover_nocut']).append(sub)
            # with slits: any spanning tree
            found=False
            for m in range(len(sub)-1,len(E)+1):
                for es in itertools.combinations(E,m):
                    if not connected(sub,es): continue
                    f=fold(sub,es)
                    if f is not None and len(set(f.values()))==6:
                        res['cover_withslits'].append((sub,es)); found=True; break
                if found: break
    return res
