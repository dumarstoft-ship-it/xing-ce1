"""Q49 立体拼合：把题图读成小立方体坐标 (x 向右, y 向后, z 向上)，穷举旋转+平移，检验能否拼成目标体。
坐标由题图逐格读出（斜二测：每个正方体正面18px，纵深方向每格向左上偏移9px）。
"""
from itertools import product

# 目标：底层 3(宽)x4(深) 满铺，上层只有左边两列 2x4，共20块
TARGET = {(x, y, 0) for x in range(3) for y in range(4)} | {(x, y, 1) for x in range(2) for y in range(4)}

P1 = {(0, 0, 0), (0, 1, 0), (0, 2, 0), (1, 2, 0), (2, 2, 0), (2, 1, 0), (2, 0, 0), (1, 2, 1)}  # U形底座+后中上方1块，8块
P2 = {(1, 0, 0), (1, 0, 1), (0, 0, 1), (0, 1, 1)}                                           # 空间扭转四连块，4块
P3 = {(0, 0, 0), (1, 0, 0), (2, 0, 0), (1, 0, 1)}                                           # 竖立T形，4块
OPTS = {
    'A': {(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0)},                       # 2x2 平板，4块
    'B': {(0, 1, 0), (0, 1, 1), (1, 1, 0), (2, 1, 0), (1, 0, 0)},            # 5块
    'C': {(0, 1, 0), (1, 1, 0), (1, 0, 0)},                                  # 3块
    'D': {(0, 2, 0), (1, 2, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)},            # 5块
}


def rotations():
    """24 proper rotations as functions on (x,y,z)."""
    mats = []
    for perm in ((0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)):
        for signs in product((1, -1), repeat=3):
            m = [[0] * 3 for _ in range(3)]
            for i in range(3):
                m[i][perm[i]] = signs[i]
            det = (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
                   - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
                   + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))
            if det == 1:
                mats.append(m)
    return mats


ROTS = rotations()
assert len(ROTS) == 24


def orient(piece):
    out = set()
    for m in ROTS:
        pts = [tuple(sum(m[i][j] * p[j] for j in range(3)) for i in range(3)) for p in piece]
        mn = [min(p[i] for p in pts) for i in range(3)]
        out.add(frozenset(tuple(p[i] - mn[i] for i in range(3)) for p in pts))
    return out


def placements(piece, target):
    res = []
    for o in orient(piece):
        for dx in range(-3, 4):
            for dy in range(-4, 5):
                for dz in range(-2, 3):
                    s = frozenset((x + dx, y + dy, z + dz) for x, y, z in o)
                    if s <= target:
                        res.append(s)
    return list(set(res))


def solve(pieces, target):
    if sum(len(p) for p in pieces) != len(target):
        return []
    pl = [placements(p, target) for p in pieces]
    sols = []

    def rec(i, used, chosen):
        if i == len(pieces):
            if used == target:
                sols.append(list(chosen))
            return
        for s in pl[i]:
            if not (s & used):
                rec(i + 1, used | s, chosen + [s])
    rec(0, frozenset(), [])
    return sols


if __name__ == '__main__':
    print('target cubes:', len(TARGET), '| given pieces:', len(P1), len(P2), len(P3))
    for k, q in OPTS.items():
        sols = solve([P1, P2, P3, q], frozenset(TARGET))
        print('option', k, 'cubes=%d' % len(q), 'tilings found:', len(sols))
        if sols:
            s = sols[0]
            names = ['P1', 'P2', 'P3', k]
            grid = {}
            for n, cells in zip(names, s):
                for c in cells:
                    grid[c] = n
            for z in (1, 0):
                print('  layer z=%d (rows y=3..0 back->front, cols x=0..2):' % z)
                for y in (3, 2, 1, 0):
                    print('   ', ' '.join(grid.get((x, y, z), '..').ljust(2) for x in range(3)))
