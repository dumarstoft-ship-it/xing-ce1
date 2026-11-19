"""M10 第49题（GD2020-XJ-Q043）：两块已知立体 + 一个选项 拼成 3×3×3 立方体。

坐标：x 向右，y 向里（纵深），z 向上；按题图斜二测画法逐块读出。
被遮住、看不见的位置单独列为 hidden，枚举“有/无”两种情况。
"""
import itertools

def rotations():
    # 24 个旋转矩阵（行列式为 +1 的置换矩阵带符号）
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
assert len(ROT) == 24

def apply(m, p):
    return tuple(sum(m[i][j]*p[j] for j in range(3)) for i in range(3))

def normalize(cells):
    mn = [min(c[i] for c in cells) for i in range(3)]
    return frozenset(tuple(c[i]-mn[i] for i in range(3)) for c in cells)

def orientations(cells):
    return {normalize([apply(m, c) for c in cells]) for m in ROT}

def placements(cells, n=3):
    out = set()
    for o in orientations(cells):
        ext = [max(c[i] for c in o) for i in range(3)]
        if any(e >= n for e in ext):
            continue
        for d in itertools.product(*[range(n-e) for e in ext]):
            out.add(frozenset(tuple(c[i]+d[i] for i in range(3)) for c in o))
    return out

def extent(cells):
    return tuple(max(c[i] for c in cells)-min(c[i] for c in cells)+1 for i in range(3))

# 左块：x=0 一面除 (0,2,2) 外全有，x=1 只有底层一排；(0,1,0)(0,2,0) 被挡住
L_vis = {(0,0,0),(0,0,1),(0,0,2),(0,1,1),(0,1,2),(0,2,1),(1,0,0),(1,1,0),(1,2,0)}
L_hid = [(0,1,0),(0,2,0)]
# 右块：前面横 2 块，向里 3 块，再向下 3 块，共 6 块，无遮挡位置
R = {(0,0,2),(1,0,2),(1,1,2),(1,2,2),(1,2,1),(1,2,0)}

OPT = {
 'A': ({(0,2,2),(1,1,2),(1,2,2),(1,1,1),(2,0,1),(2,0,0),(2,1,1),(3,1,1),(2,1,0)}, [(1,2,1),(1,2,0)]),
 'B': ({(0,2,2),(1,1,2),(1,2,2),(1,1,1),(2,0,1),(2,0,0),(2,1,1),(2,1,0)}, [(1,2,1),(1,2,0)]),
 'C': ({(0,2,2),(1,1,2),(1,2,2),(1,0,1),(2,0,1),(2,0,0),(2,1,1),(2,1,0)}, [(1,1,1),(1,2,1),(1,2,0)]),
 'D': ({(0,2,2),(1,2,2),(0,2,1),(1,1,1),(1,0,1),(2,0,1),(2,0,0),(2,1,1),(2,1,0)}, [(1,2,1),(1,2,0)]),
}

def variants(vis, hid):
    for k in range(len(hid)+1):
        for sub in itertools.combinations(hid, k):
            yield set(vis) | set(sub), sub

FULL = frozenset(itertools.product(range(3), repeat=3))

for Lset, Lsub in variants(L_vis, L_hid):
    Lpl = placements(Lset)
    Rpl = placements(R)
    comps = set()
    for lp in Lpl:
        for rp in Rpl:
            if lp & rp:
                continue
            comps.add(normalize(FULL - lp - rp))
    print(f'左块隐藏块取 {Lsub}：左块{len(Lset)}块，右块{len(R)}块，余下{27-len(Lset)-len(R)}块；不同的余形 {len(comps)} 种')
    for name, (vis, hid) in OPT.items():
        print(f'  {name} 外形尺寸 {extent(vis)}', end='')
        ok = []
        for oset, osub in variants(vis, hid):
            ors = orientations(oset)
            if any(c in ors for c in comps):
                ok.append(osub)
        print(f'  可补成立方体的隐藏取法: {ok}')

# 输出 C 的一种拼法（左块按题图摆放不动）
Lset = set(L_vis) | set(L_hid)
Cset = OPT['C'][0] | {(1,1,1),(1,2,1)}
Cors = orientations(Cset)
lp = frozenset(Lset)  # 题图摆法
for rp in placements(R):
    if lp & rp:
        continue
    rest = FULL - lp - rp
    if normalize(rest) in Cors:
        print('左块按原样放，右块占:', sorted(rp))
        print('余下(应与C全等):', sorted(rest))
        # 找出把 C 转到 rest 的旋转
        for m in ROT:
            img = normalize([apply(m, c) for c in Cset])
            if img == normalize(rest):
                print('旋转矩阵', m)
                break
