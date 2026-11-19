"""S01 第49题（SYDW2024-Q067）：4块立方体组成的图形 + 一个选项 拼成完整长方体。

坐标：x 向右，y 向里，z 向上。题干图从右前上方看；选项图从右前下方看（看到底面）。
看不见的位置列为 hidden，枚举有/无。
"""
import itertools

def rotations():
    mats = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product([1, -1], repeat=3):
            m = [[0]*3 for _ in range(3)]
            for i in range(3):
                m[i][perm[i]] = signs[i]
            det = (m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])
                   - m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])
                   + m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]))
            if det == 1:
                mats.append(m)
    return mats
ROT = rotations()

def apply(m, p):
    return tuple(sum(m[i][j]*p[j] for j in range(3)) for i in range(3))
def normalize(cells):
    mn = [min(c[i] for c in cells) for i in range(3)]
    return frozenset(tuple(c[i]-mn[i] for i in range(3)) for c in cells)
def orientations(cells):
    return {normalize([apply(m, c) for c in cells]) for m in ROT}
def extent(cells):
    return tuple(max(c[i] for c in cells)-min(c[i] for c in cells)+1 for i in range(3))

# 题干：前左 (0,0,0)，其后 (0,1,0)，右边 (2,1,0)，上面一块 (1,1,1) 架在两块之间（其下 (1,1,0) 空，可见左块的右侧面）
G = {(0,0,0),(0,1,0),(1,1,1),(2,1,0)}
print('题干外形', extent(G), '块数', len(G))

OPT = {
 'A': ({(0,0,2),(1,0,2),(0,0,1),(0,0,0),(1,0,0),(1,1,2),(1,1,0)}, [(0,1,2),(0,1,1)]),
 'B': ({(0,0,2),(1,0,2),(0,0,1),(1,0,1),(1,0,0),(1,1,2),(1,1,0)}, [(0,1,2)]),
 'C': ({(1,0,2),(0,0,1),(1,0,1),(0,0,0),(1,0,0),(1,1,2),(1,1,0)}, [(0,1,1)]),
 'D': ({(0,0,2),(1,0,2),(1,0,1),(0,0,0),(1,0,0),(1,1,1),(0,1,0)}, []),
}

def boxes(total):
    for a in range(1, total+1):
        for b in range(a, total+1):
            if total % (a*b) == 0:
                c = total // (a*b)
                if c >= b:
                    yield (a, b, c)

def fits(G, O):
    total = len(G) + len(O)
    for dims in boxes(total):
        for perm in set(itertools.permutations(dims)):
            full = frozenset(itertools.product(*[range(d) for d in perm]))
            for g in orientations(G):
                ge = extent(g)
                if any(ge[i] > perm[i] for i in range(3)):
                    continue
                for d in itertools.product(*[range(perm[i]-ge[i]+1) for i in range(3)]):
                    gp = frozenset(tuple(c[i]+d[i] for i in range(3)) for c in g)
                    rest = normalize(full - gp)
                    if rest in orientations(O):
                        return perm
    return None

for name, (vis, hid) in OPT.items():
    res = []
    for k in range(len(hid)+1):
        for sub in itertools.combinations(hid, k):
            O = set(vis) | set(sub)
            r = fits(G, O)
            res.append((sub, len(O), r))
    print(name, res)
