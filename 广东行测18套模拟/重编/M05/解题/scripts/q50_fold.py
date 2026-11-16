"""Q50 展开图折叠：用程序把阶梯形展开图折成正方体，求标号棱的对应关系。
展开图（列,行）：S1(0,0) S2(1,0)* S3(1,1) S4(2,1)* S5(2,2) S6(3,2)*   (*=面上有小方框)
展开图标号：8=S1|S2 公共边，5=S3|S4 公共边，6=S5|S6 公共边，7=S4 的上边（外边）
立体图：小方框在 上(T)、前(F)、右(R) 三面；1=上后棱，2=上右棱，3=右下棱，4=前左棱
约定：展开图画的是外表面（朝向读者），折叠时各面向纸面背后折。
"""
from itertools import product
import numpy as np

net = {'S1': (0, 0), 'S2': (1, 0), 'S3': (1, 1), 'S4': (2, 1), 'S5': (2, 2), 'S6': (3, 2)}
marked = {'S2', 'S4', 'S6'}

# 折叠：每个面记录 (外法向 n, 展开图向右方向 u, 展开图向下方向 v)
frames = {'S3': (np.array([0, 0, 1]), np.array([1, 0, 0]), np.array([0, -1, 0]))}
pos2name = {v: k for k, v in net.items()}
stack = ['S3']
while stack:
    f = stack.pop()
    n, u, v = frames[f]
    c, r = net[f]
    for (dc, dr) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nb = pos2name.get((c + dc, r + dr))
        if nb is None or nb in frames:
            continue
        if (dc, dr) == (1, 0):
            frames[nb] = (u, -n, v)
        elif (dc, dr) == (-1, 0):
            frames[nb] = (-u, n, v)
        elif (dc, dr) == (0, 1):
            frames[nb] = (v, u, -n)
        else:
            frames[nb] = (-v, u, n)
        stack.append(nb)

normal = {k: tuple(int(x) for x in frames[k][0]) for k in frames}
assert len(set(normal.values())) == 6


def side_normal(face, side):
    n, u, v = frames[face]
    d = {'right': u, 'left': -u, 'down': v, 'up': -v}[side]
    return tuple(int(x) for x in d)


net_edges = {
    8: frozenset([normal['S1'], normal['S2']]),
    5: frozenset([normal['S3'], normal['S4']]),
    6: frozenset([normal['S5'], normal['S6']]),
    7: frozenset([normal['S4'], side_normal('S4', 'up')]),
}

# 立体图坐标：x 向右，y 向后，z 向上
T, F, R = (0, 0, 1), (0, -1, 0), (1, 0, 0)
Bk, Bt, L = (0, 1, 0), (0, 0, -1), (-1, 0, 0)
cube_edges = {1: frozenset([T, Bk]), 2: frozenset([T, R]), 3: frozenset([R, Bt]), 4: frozenset([F, L])}


def rotations():
    mats = []
    for perm in ((0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)):
        for signs in product((1, -1), repeat=3):
            m = np.zeros((3, 3), int)
            for i in range(3):
                m[i][perm[i]] = signs[i]
            if round(np.linalg.det(m)) == 1:
                mats.append(m)
    return mats


options = {'A': {1: 7, 2: 5, 3: 6, 4: 8}, 'B': {1: 6, 2: 5, 3: 8, 4: 7},
           'C': {1: 5, 2: 7, 3: 8, 4: 6}, 'D': {1: 5, 2: 7, 3: 6, 4: 8}}

found = []
for m in rotations():
    rot = lambda p: tuple(int(x) for x in m @ np.array(p))
    if {rot(normal[s]) for s in marked} != {T, F, R}:
        continue
    corr = {}
    for k, e in net_edges.items():
        img = frozenset(rot(p) for p in e)
        for c, ce in cube_edges.items():
            if ce == img:
                corr[c] = k
    found.append(corr)
    print('rotation consistent with marks -> cube edge : net edge', dict(sorted(corr.items())))

for k, opt in options.items():
    ok = any(all(corr.get(c) == n for c, n in opt.items()) for corr in found)
    print('option', k, opt, 'consistent:', ok)

# 若把展开图当成从内侧看（镜像），再检验一次，说明D是镜像干扰项
print('--- mirror check (net viewed from inside) ---')
mirror = lambda p: (-p[0], p[1], p[2])
for m in rotations():
    rot = lambda p: tuple(int(x) for x in m @ np.array(mirror(p)))
    if {rot(normal[s]) for s in marked} != {T, F, R}:
        continue
    corr = {}
    for k, e in net_edges.items():
        img = frozenset(rot(p) for p in e)
        for c, ce in cube_edges.items():
            if ce == img:
                corr[c] = k
    if len(corr) == 4:
        print('mirror full correspondence:', dict(sorted(corr.items())))
