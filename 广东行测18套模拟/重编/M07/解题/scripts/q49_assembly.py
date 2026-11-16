"""Q49 立体拼合核验.
坐标: x向右, y向上, z向里(远离观察者). 整体由正面图读出 16 个可见方块, 第17个(0,0,1)在两面图中都被遮住
(用渲染比对确认: 整体包围盒内只有这个位置在正、反两面图中都看不到).
枚举①②的24种旋转和全部平移, 要求灰块落在灰块上, 求剩余部分③, 再与四个选项(按图读出的结构)做旋转比对.
"""
import itertools
W,G='w','g'
S={}
for p in [(0,0,0),(-2,0,1),(-1,0,1),(0,0,1),(1,0,1),(-2,0,2),(-1,0,2),(1,0,2),
          (-1,1,1),(0,1,1),(0,1,2),(1,1,2),(-1,2,1),(0,2,2)]: S[p]=W
for p in [(0,1,0),(-2,1,2),(0,0,2)]: S[p]=G
assert len(S)==17 and sum(v==G for v in S.values())==3
P1={(0,0,0):W,(0,1,0):G,(0,0,1):W,(1,0,1):W,(1,0,2):W}
P2={(0,0,0):W,(0,1,0):G,(1,0,0):W,(1,0,1):W,(1,1,1):W,(1,2,1):W}

def rotations():
    # all 24 proper rotations as 3x3 integer matrices
    mats=[]
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product([1,-1],repeat=3):
            M=[[0]*3 for _ in range(3)]
            for i in range(3): M[i][perm[i]]=signs[i]
            # determinant
            d=(M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1])-M[0][1]*(M[1][0]*M[2][2]-M[1][2]*M[2][0])+M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0]))
            if d==1: mats.append(M)
    return mats
ROTS=rotations(); assert len(ROTS)==24
def apply(M,p): return tuple(sum(M[i][j]*p[j] for j in range(3)) for i in range(3))
def norm(piece):
    mn=[min(p[i] for p in piece) for i in range(3)]
    return {tuple(p[i]-mn[i] for i in range(3)):c for p,c in piece.items()}
def orientations(piece):
    seen=[];out=[]
    for M in ROTS:
        q=norm({apply(M,p):c for p,c in piece.items()})
        key=frozenset(q.items())
        if key not in seen: seen.append(key); out.append(q)
    return out
def placements(piece, target):
    res=[]
    for q in orientations(piece):
        for t in itertools.product(range(-4,4),repeat=3):
            cells={(p[0]+t[0],p[1]+t[1],p[2]+t[2]):c for p,c in q.items()}
            if all(c2 in target and target[c2]==c for c2,c in cells.items()):
                k=frozenset(cells)
                if k not in [frozenset(r) for r in res]: res.append(cells)
    return res
rems=[]
for a in placements(P1,S):
    for b in placements(P2,S):
        if set(a)&set(b): continue
        R={p:c for p,c in S.items() if p not in a and p not in b}
        rems.append((a,b,R))
print('number of (①,②) placements leaving a remainder:',len(rems))
def connected(R):
    cells=set(R); start=next(iter(cells)); seen={start}; st=[start]
    while st:
        p=st.pop()
        for d in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
            q=(p[0]+d[0],p[1]+d[1],p[2]+d[2])
            if q in cells and q not in seen: seen.add(q); st.append(q)
    return len(seen)==len(cells)
uniq=[]
for a,b,R in rems:
    print('①',sorted(a)); print('②',sorted(b)); print('③',sorted(R.items()),'connected:',connected(R))
    uniq.append(R)
# Options read from the figure (each in its own coordinates; render-compared against the image)
OPT={
 'A':{(0,0,0):G,(1,0,0):W,(2,0,0):W,(0,1,0):W,(0,2,0):W,(0,1,-1):W},
 'B':{(0,0,0):G,(1,0,0):W,(-1,1,0):W,(0,1,0):W,(0,2,0):W,(0,1,1):W},
 'C':{(0,0,0):W,(0,1,0):W,(1,0,0):W,(2,0,0):G,(1,0,-1):W,(1,-1,0):W},
 'D':{(0,0,0):W,(1,0,0):G,(2,0,0):W,(0,1,0):W,(0,2,0):W,(0,1,-1):W},
}
target=[frozenset(norm(R).items()) for R in uniq]
for k,o in OPT.items():
    ok=any(frozenset(q.items()) in target for q in orientations(o))
    print(k, len(o),'cubes', sum(v==G for v in o.values()),'gray', '-> matches ③ (proper rotation)' if ok else '-> no match')
# 只看形状不看颜色（用于说明易错项）：
def shape_set(o): return frozenset(o)
tshape=[frozenset(norm({p:W for p in R}).keys()) for R in uniq]
def mirror(o): return {(-p[0],p[1],p[2]):c for p,c in o.items()}
for k,o in OPT.items():
    same_shape=any(frozenset(q.keys()) in tshape for q in orientations(o))
    mirror_shape=any(frozenset(q.keys()) in tshape for q in orientations(mirror(o)))
    mirror_color=any(frozenset(q.items()) in target for q in orientations(mirror(o)))
    print(k,'shape-only match:',same_shape,'| mirror-shape match:',mirror_shape,'| mirror with colors:',mirror_color)
