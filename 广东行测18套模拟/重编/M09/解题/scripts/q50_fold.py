# -*- coding: utf-8 -*-
"""M09 第50题（GD2021-XZ-Q053）：四个展开图（含半个正方形的直角三角形）能否折成立方体。

做法：按题图（3倍放大后逐点读取）把每个选项写成网格坐标上的多边形（单位正方形、等腰直角三角形），
两块多边形有一条公共边就是一条折线。以第一块正方形为底面，沿生成树逐块向同一侧折90°，
求出每块在立方体上的位置；再检查：①不在生成树上的公共边，两侧折出来是否落在同一条棱上；
②立方体6个面上每一点被覆盖几次（应恰为1次）。
"""
import itertools
from collections import deque
import numpy as np

def sq(c, r):
    return [(c, r), (c + 1, r), (c + 1, r + 1), (c, r + 1)]

# 网格坐标：x向右、y向下，1个单位＝1个小正方形的边长
NETS = {
    "A": {"上方正方形": sq(1, 0), "中1": sq(0, 1), "中2": sq(1, 1), "中3": sq(2, 1), "中4": sq(3, 1),
          "左下三角": [(2, 2), (3, 2), (3, 3)], "右下三角": [(3, 2), (4, 2), (3, 3)]},
    "B": {"中1": sq(0, 1), "中2": sq(1, 1), "中3": sq(2, 1), "中4": sq(3, 1), "下方正方形": sq(2, 2),
          "左上三角": [(0, 0), (0, 1), (1, 1)], "右上三角": [(3, 0), (3, 1), (4, 1)]},
    "C": {"中1": sq(0, 2), "中2": sq(1, 2), "中3": sq(2, 2), "上方正方形": sq(1, 1), "下方正方形": sq(2, 3),
          "顶上三角": [(1, 0), (1, 1), (2, 1)], "右侧三角": [(3, 2), (3, 3), (4, 3)]},
    "D": {"中1": sq(0, 1), "中2": sq(1, 1), "中3": sq(2, 1), "左下正方形": sq(0, 2), "右上正方形": sq(3, 0),
          "右侧三角": [(3, 1), (4, 1), (3, 2)], "左下三角": [(0, 3), (1, 3), (0, 4)]},
}


def edges(poly):
    return [frozenset((poly[i], poly[(i + 1) % len(poly)])) for i in range(len(poly))]


def fold(net):
    names = list(net)
    adj = {n: [] for n in names}
    shared = []
    for a, b in itertools.combinations(names, 2):
        for e in set(edges(net[a])) & set(edges(net[b])):
            adj[a].append((b, e)); adj[b].append((a, e)); shared.append((a, b, e))
    base = names[0] if len(net[names[0]]) == 4 else next(n for n in names if len(net[n]) == 4)
    # 每块的映射：网格点 p -> O + (p-p0)在两个面内方向上的分量；记 (p0, O, ex, ey, n)
    # ex、ey 是网格x、y方向在三维中的单位向量，n 是指向立方体内部的法向
    maps = {base: (np.array(net[base][0], float), np.array([0., 0., 0.]),
                   np.array([1., 0., 0.]), np.array([0., 1., 0.]), np.array([0., 0., 1.]))}
    tree = set()
    q = deque([base])
    while q:
        a = q.popleft()
        p0, O, ex, ey, n = maps[a]
        for b, e in adj[a]:
            if b in maps:
                continue
            u0, u1 = [np.array(v, float) for v in e]
            # 折线方向 d（网格内），以及从 a 指向 b 的面内垂直方向 w
            d = (u1 - u0) / np.linalg.norm(u1 - u0)
            perp = np.array([-d[1], d[0]])
            cb = np.mean(np.array(net[b], float), axis=0)
            if np.dot(cb - u0, perp) < 0:
                perp = -perp
            # 三维中：网格方向 g 的像 = g_x*ex + g_y*ey
            D3 = d[0] * ex + d[1] * ey
            W3 = perp[0] * ex + perp[1] * ey
            # 折起后：w 方向变成 a 的内法向 n；b 的内法向变成 -W3
            def img(g, D3=D3, W3=W3, n=n, d=d, perp=perp):
                return np.dot(g, d) * D3 + np.dot(g, perp) * n
            ex_b, ey_b = img(np.array([1., 0.])), img(np.array([0., 1.]))
            Ou0 = O + (u0 - p0)[0] * ex + (u0 - p0)[1] * ey
            maps[b] = (u0, Ou0, ex_b, ey_b, -W3)
            tree.add(frozenset((a, b)))
            q.append(b)

    def to3(name, p):
        p0, O, ex, ey, n = maps[name]
        g = np.array(p, float) - p0
        return O + g[0] * ex + g[1] * ey

    # 平移到 [0,1]^3
    allpts = np.array([to3(nm, p) for nm in names for p in net[nm]])
    shift = -allpts.min(axis=0)
    pts3 = {nm: [tuple(int(round(v)) for v in to3(nm, p) + shift) for p in net[nm]] for nm in names}
    # ①非生成树的公共边是否一致
    torn = []
    for a, b, e in shared:
        if frozenset((a, b)) in tree:
            continue
        ea = sorted(tuple(int(round(x)) for x in to3(a, v) + shift) for v in e)
        eb = sorted(tuple(int(round(x)) for x in to3(b, v) + shift) for v in e)
        if ea != eb:
            torn.append((a, b, ea, eb))
    # ②各面覆盖次数
    N = 60
    grid = (np.arange(N) + 0.5) / N
    cover = {}
    for axis in range(3):
        for val in (0.0, 1.0):
            others = [i for i in range(3) if i != axis]
            cnt = np.zeros((N, N), int)
            for nm in names:
                P = np.array(pts3[nm])
                if not np.allclose(P[:, axis], val):
                    continue
                poly = P[:, others]
                X, Y = np.meshgrid(grid, grid, indexing="ij")
                inside = np.zeros_like(X, bool)
                m = len(poly)
                for i in range(m):   # 射线法
                    x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % m]
                    cond = ((y1 > Y) != (y2 > Y))
                    xint = (x2 - x1) * (Y - y1) / np.where(y2 - y1 == 0, 1e-12, y2 - y1) + x1
                    inside ^= cond & (X < xint)
                cnt += inside
            cover[("xyz"[axis], int(val))] = cnt
    return pts3, torn, cover


if __name__ == "__main__":
    for k, net in NETS.items():
        pts3, torn, cover = fold(net)
        ok = all((c == 1).all() for c in cover.values()) and not torn
        print(f"== 选项{k}：{'能' if ok else '不能'}折成立方体")
        for nm, P in pts3.items():
            if len(P) == 3:
                print(f"   {nm} 折到：{P}")
        for f, c in cover.items():
            if not (c == 1).all():
                print(f"   面 {f[0]}={f[1]}：未覆盖 {(c == 0).mean():.0%}，重叠 {(c >= 2).mean():.0%}")
        for a, b, ea, eb in torn:
            print(f"   {a} 与 {b} 的公共边折后不重合：{ea} vs {eb}")
