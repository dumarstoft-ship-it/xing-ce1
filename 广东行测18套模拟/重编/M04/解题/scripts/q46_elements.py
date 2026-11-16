# -*- coding: utf-8 -*-
"""Q46 读图：六边形内三个元素（圆、三角形、短线）的位置与方向。

做法：
1. 每个格子里找到六边形外框的6个顶点（取边框像素的极值点），
2. 删掉六边形外框像素后，剩下的连通块分为：圆（环状，有内孔）、三角形（与外框粘连的部分，用原图减去六边形后找）、短线（细长块）；
3. 圆：圆心到6条边的距离，取最近的边；
4. 三角形：三角形贴着哪个顶点、哪条边（取三角形像素中离六边形顶点最近的那个顶点，以及与三角形重合的边）；
5. 短线：PCA 求方向角。
边编号（顺时针）：e0=上边，e1=右上边，e2=右下边，e3=下边，e4=左下边，e5=左上边。
顶点编号（顺时针）：v0=左上，v1=右上，v2=右，v3=右下，v4=左下，v5=左。
"""
import sys
import numpy as np
from PIL import Image

IMG = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s19_p12_i00.png'
a = np.array(Image.open(IMG).convert('L')).astype(int)
dark = a < 140

boxes = {
    '图1': (10, 9, 104, 107), '图2': (107, 9, 202, 107), '图3': (204, 9, 299, 107),
    '图4': (301, 9, 396, 107), '图5': (399, 9, 494, 107),
    'A': (106, 136, 201, 233), 'B': (203, 136, 299, 233), 'C': (301, 136, 396, 233), 'D': (398, 136, 493, 233),
}


def label(mask):
    """4-连通标号（不依赖 scipy）。"""
    h, w = mask.shape
    lab = np.zeros((h, w), int)
    n = 0
    for y in range(h):
        for x in range(w):
            if mask[y, x] and lab[y, x] == 0:
                n += 1
                stack = [(y, x)]
                lab[y, x] = n
                while stack:
                    cy, cx = stack.pop()
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and lab[ny, nx] == 0:
                            lab[ny, nx] = n
                            stack.append((ny, nx))
    return lab, n


def hexagon(m):
    """用行/列投影求六边形：上下两条水平边的 y、左右两顶点的 x。"""
    ys, xs = np.nonzero(m)
    rows = m.sum(axis=1)
    # 水平边：像素最多的两行附近
    top_y = ys.min()
    bot_y = ys.max()
    left_x = xs.min()
    right_x = xs.max()
    # 上边的左右端点
    row_top = np.nonzero(m[top_y:top_y + 3].any(axis=0))[0]
    row_bot = np.nonzero(m[bot_y - 2:bot_y + 1].any(axis=0))[0]
    # 左右顶点的 y：最左列像素的平均 y
    ly = np.nonzero(m[:, left_x:left_x + 2].any(axis=1))[0].mean()
    ry = np.nonzero(m[:, right_x - 1:right_x + 1].any(axis=1))[0].mean()
    return top_y + 1, bot_y - 1, left_x + 1, right_x - 1, ly, ry


def seg_dist(p, a_, b_):
    p, a_, b_ = map(np.asarray, (p, a_, b_))
    ab = b_ - a_
    t = np.clip(np.dot(p - a_, ab) / np.dot(ab, ab), 0, 1)
    return np.linalg.norm(p - (a_ + t * ab))


def analyse(name, box):
    x0, y0, x1, y1 = box
    sub = dark[y0:y1, x0:x1]
    lab, n = label(sub)
    # 最大连通块 = 六边形 + 贴边的三角形/圆
    sizes = [(lab == i).sum() for i in range(1, n + 1)]
    big = int(np.argmax(sizes)) + 1
    hexm = lab == big
    ty, by, lx, rx, ly, ry = hexagon(hexm)
    cy = (ty + by) / 2
    # 六边形顶点：上边两端取上边像素的左右端（但三角形可能贴在上边，所以用对称性推）：
    # 正六边形平顶：上边长 = 半宽；顶点 x = cx ± R/2
    cx = (lx + rx) / 2
    R = (rx - lx) / 2
    V = [(cx - R / 2, ty), (cx + R / 2, ty), (rx, cy), (cx + R / 2, by), (cx - R / 2, by), (lx, cy)]
    E = [(V[i], V[(i + 1) % 6]) for i in range(6)]
    # 把六边形边框（距边 <=2.2 像素）抹掉，剩下的就是元素
    rest = sub.copy()
    H, W = sub.shape
    for y in range(H):
        for x in range(W):
            if sub[y, x] and min(seg_dist((x, y), *e) for e in E) <= 2.2:
                rest[y, x] = False
    lab2, n2 = label(rest)
    out = []
    for i in range(1, n2 + 1):
        m = lab2 == i
        cnt = m.sum()
        if cnt < 6:
            continue
        ys, xs = np.nonzero(m)
        pts = np.stack([xs, ys], 1).astype(float)
        c = pts.mean(0)
        cov = np.cov((pts - c).T)
        ev, evec = np.linalg.eigh(cov)
        elong = ev[1] / max(ev[0], 1e-6)
        # 是否有内孔（圆环）
        bb = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        holes, nh = label(~bb)
        inner = 0
        for j in range(1, nh + 1):
            hm = holes == j
            hy, hx = np.nonzero(hm)
            if hy.min() > 0 and hx.min() > 0 and hy.max() < bb.shape[0] - 1 and hx.max() < bb.shape[1] - 1:
                inner += hm.sum()
        out.append(dict(cnt=int(cnt), c=c, elong=elong, evec=evec[:, 1], inner=inner,
                        bbox=(xs.min(), ys.min(), xs.max(), ys.max())))
    return V, E, out


def nearest_edge(p, E):
    d = [seg_dist(p, *e) for e in E]
    i = int(np.argmin(d))
    return i, d[i]


EN = ['e0上边', 'e1右上边', 'e2右下边', 'e3下边', 'e4左下边', 'e5左上边']
VN = ['v0左上', 'v1右上', 'v2右', 'v3右下', 'v4左下', 'v5左']

if __name__ == '__main__':
    for name, box in boxes.items():
        V, E, comps = analyse(name, box)
        print('==', name)
        for c in comps:
            kind = '圆' if c['inner'] > 20 else ('线' if c['elong'] > 8 else '三角/其他')
            desc = ''
            if kind == '圆':
                i, d = nearest_edge(c['c'], E)
                desc = '圆心最近边 %s 距离 %.1f' % (EN[i], d)
            elif kind == '线':
                vx, vy = c['evec']
                ang = np.degrees(np.arctan2(-vy, vx)) % 180
                desc = '方向角 %.0f°（0=水平, 60=“/”, 120=“\\”）' % ang
            else:
                # 三角形：找离它最近的六边形顶点，以及它贴着的边
                bx0, by0, bx1, by1 = c['bbox']
                dv = [min(np.hypot(x - V[k][0], y - V[k][1]) for x in (bx0, bx1) for y in (by0, by1)) for k in range(6)]
                k = int(np.argmin(dv))
                desc = '最近顶点 %s (%.1f)  bbox=%s centroid=(%.1f,%.1f)' % (VN[k], dv[k], c['bbox'], c['c'][0], c['c'][1])
            print('  %-6s n=%3d inner=%3d elong=%5.1f  %s' % (kind, c['cnt'], c['inner'], c['elong'], desc))
