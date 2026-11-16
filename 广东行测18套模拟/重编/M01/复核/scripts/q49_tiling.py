"""第49题：多面体拼合枚举。
坐标 (i, j, k)：i 向右，j 向上，k 向后（远离观察者）。题图为斜二测，向后一格 = 画面右上偏移。

题干多面体（由前视图 + 后视图读出；后视图 = 绕竖轴转 180°，i' = 2 - i, k' = 2 - k）：
  j=0: (0,0,0) (1,0,0) | (-1,0,1) (0,0,1) (1,0,1) (2,0,1) | (0,0,2) (1,0,2) (2,0,2)
  j=1: (0,1,1) (1,1,1)G | (0,1,2) (1,1,2) (2,1,2)G
  j=2: (1,2,1)G (1,2,2)
  其中 (0,0,1) (1,0,1) 两块前后都看不到，由“共16块”推出存在。13白3灰，与题干一致。

选项（各自坐标，k=-1 表示在前一排）：
  A: (0,1,0) (1,1,0) (1,0,0) (2,0,0) 白, (2,0,-1) 灰                         5块
  B: (0,1,0) (0,0,-1) 白, (1,0,0) 灰, (0,0,0) 被挡住（连通必需，颜色未知）     4块
  C: (0,0,0) (0,1,0) (0,2,0) (1,1,0) (1,0,0) (1,0,-1) 白, (0,2,-1) 灰          7块
  D: (0,2,0) (0,1,0) (0,0,0) (0,1,-1) (-1,1,0) (-1,0,0) 白, (0,0,-1) 灰        7块
只允许旋转（24 种），不允许镜像；另附“允许镜像”的结果作参考。
"""
import itertools

W, G, U = "W", "G", "?"  # U: 颜色未知
P = {
    (0, 0, 0): W, (1, 0, 0): W, (-1, 0, 1): W, (0, 0, 1): W, (1, 0, 1): W, (2, 0, 1): W,
    (0, 0, 2): W, (1, 0, 2): W, (2, 0, 2): W,
    (0, 1, 1): W, (1, 1, 1): G, (0, 1, 2): W, (1, 1, 2): W, (2, 1, 2): G,
    (1, 2, 1): G, (1, 2, 2): W,
}
OPT = {
    "A": {(0, 1, 0): W, (1, 1, 0): W, (1, 0, 0): W, (2, 0, 0): W, (2, 0, -1): G},
    "B": {(0, 1, 0): W, (0, 0, -1): W, (1, 0, 0): G, (0, 0, 0): U},
    "C": {(0, 0, 0): W, (0, 1, 0): W, (0, 2, 0): W, (1, 1, 0): W, (1, 0, 0): W, (1, 0, -1): W, (0, 2, -1): G},
    "D": {(0, 2, 0): W, (0, 1, 0): W, (0, 0, 0): W, (0, 1, -1): W, (-1, 1, 0): W, (-1, 0, 0): W, (0, 0, -1): G},
}
assert len(P) == 16 and sum(v == G for v in P.values()) == 3


def det3(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def all_mats(allow_mirror):
    mats = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1, -1), repeat=3):
            m = [[0] * 3 for _ in range(3)]
            for r in range(3):
                m[r][perm[r]] = signs[r]
            if allow_mirror or det3(m) == 1:
                mats.append(m)
    return mats


def apply(m, p):
    return tuple(sum(m[r][c] * p[c] for c in range(3)) for r in range(3))


def placements(piece, mats):
    """所有落在 P 内且颜色相容的放置，返回 frozenset(格子) 列表（去重）。"""
    out = set()
    for m in mats:
        rot = {apply(m, p): col for p, col in piece.items()}
        anchor = min(rot)
        for target in P:
            d = tuple(t - a for t, a in zip(target, anchor))
            cells = {tuple(x + y for x, y in zip(p, d)): col for p, col in rot.items()}
            if all(c in P and (col == U or P[c] == col) for c, col in cells.items()):
                out.add(frozenset(cells))
    return out


def solve(names, allow_mirror):
    mats = all_mats(allow_mirror)
    pl = [placements(OPT[n], mats) for n in names]
    sols = []
    for combo in itertools.product(*pl):
        cells = set()
        ok = True
        for s in combo:
            if cells & s:
                ok = False
                break
            cells |= s
        if ok and cells == set(P):
            sols.append(combo)
    return sols, [len(x) for x in pl]


for allow_mirror in (False, True):
    print("允许镜像" if allow_mirror else "只允许旋转")
    for trio in itertools.combinations("ABCD", 3):
        n = sum(len(OPT[t]) for t in trio)
        if n != 16:
            print(f"  {''.join(trio)}: 块数 {n} != 16，不可能")
            continue
        sols, counts = solve(trio, allow_mirror)
        print(f"  {''.join(trio)}: 块数16，各自合法放置数 {counts}，拼成方案数 {len(sols)}")
        for s in sols[:4]:
            for name, cells in zip(trio, s):
                print("     ", name, sorted(cells))
            print("      ---")
