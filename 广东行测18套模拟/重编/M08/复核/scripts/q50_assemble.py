"""第50题：由正、反两面直观图重建18块的立体（x向右、y向后、z向上），
再用①、②（各种旋转+平移，颜色须对应）去拼，剩下的部分与四个选项（含旋转）比对。
②在图中有一块可能被遮住的位置(0,1,0)，两种情况都试；选项B同理有被遮住的(0,1,0)。"""
from itertools import product

W, G = 'W', 'G'
S = {
 (0,0,0):W,(1,0,0):W,(0,1,0):W,(1,1,0):W,(2,1,0):W,(0,2,0):W,(1,2,0):W,(2,2,0):W,
 (1,0,1):G,(1,1,1):W,(2,1,1):G,(0,2,1):W,(1,2,1):W,(2,2,1):W,
 (1,0,2):W,(1,1,2):W,(0,2,2):W,(1,2,2):G,
}
assert len(S) == 18 and sum(v == G for v in S.values()) == 3

P1 = {(0,1,0):W,(1,0,0):W,(2,0,0):W,(2,0,1):G,(1,1,0):W,(2,1,0):W,(2,1,1):W}
P2_base = {(0,0,0):W,(0,0,1):W,(0,1,1):G,(1,1,0):W,(1,1,1):W}
P2_variants = {'5块': P2_base, '6块(含被遮(0,1,0))': {**P2_base, (0,1,0):W}}
OPTS = {
 'A': [{(0,0,0):W,(1,0,0):G,(2,0,0):W,(2,0,1):W,(0,1,0):W}],
 'B': [{(0,0,0):W,(0,0,1):W,(1,1,0):G,(2,1,0):W,(0,1,0):W}],  # (0,1,0) hidden, needed for connectivity
 'C': [{(0,0,0):W,(1,0,0):W,(0,1,0):W,(1,1,0):W,(1,1,1):G,(1,1,2):W}],
 'D': [{(0,1,0):W,(1,1,0):W,(2,1,0):W,(2,0,0):G,(2,1,1):W}],
}

def rotations():
    # all 24 proper rotations as functions on (x,y,z)
    import itertools
    mats = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product([1,-1], repeat=3):
            m = [[0]*3 for _ in range(3)]
            for i in range(3):
                m[i][perm[i]] = signs[i]
            # determinant
            det = (m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1]) - m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0]) + m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]))
            if det == 1:
                mats.append(m)
    return mats
ROT = rotations()
assert len(ROT) == 24

def apply(m, p):
    return tuple(sum(m[i][j]*p[j] for j in range(3)) for i in range(3))

def normalize(piece):
    mn = [min(p[i] for p in piece) for i in range(3)]
    return frozenset((tuple(p[i]-mn[i] for i in range(3)), c) for p, c in piece.items())

def orientations(piece):
    out = set()
    for m in ROT:
        out.add(normalize({apply(m, p): c for p, c in piece.items()}))
    return out

def placements(piece, target):
    """all ways to place piece inside target (dict) with matching colours"""
    res = []
    for o in orientations(piece):
        cells = list(o)
        for dx, dy, dz in product(range(-3, 4), repeat=3):
            ok = True; placed = {}
            for (p, c) in cells:
                q = (p[0]+dx, p[1]+dy, p[2]+dz)
                if target.get(q) != c:
                    ok = False; break
                placed[q] = c
            if ok:
                res.append(placed)
    # dedupe
    uniq = {frozenset(p.items()): p for p in res}
    return list(uniq.values())

opt_orients = {k: set().union(*[orientations(v) for v in vs]) for k, vs in OPTS.items()}
def connected(cells):
    cells = set(cells); start = next(iter(cells)); seen = {start}; st = [start]
    while st:
        x, y, z = st.pop()
        for d in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
            q = (x+d[0], y+d[1], z+d[2])
            if q in cells and q not in seen:
                seen.add(q); st.append(q)
    return len(seen) == len(cells)

for name2, P2 in P2_variants.items():
    p1s = placements(P1, S)
    print(f'②={name2}: ①在立体中的放法 {len(p1s)} 种')
    for pl1 in p1s:
        rest1 = {k: v for k, v in S.items() if k not in pl1}
        for pl2 in placements(P2, rest1):
            rest = {k: v for k, v in rest1.items() if k not in pl2}
            n = normalize(rest)
            match = [k for k, os in opt_orients.items() if n in os]
            print('  ①:', sorted(pl1), '\n  ②:', sorted(pl2), '\n  ③剩余:', sorted(rest.items()), '连通' if connected(rest) else '不连通', '-> 匹配选项', match)
