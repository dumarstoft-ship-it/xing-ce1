# -*- coding: utf-8 -*-
"""Q46 读图：六边形内三个元素（圆、三角形、短线）的位置与方向，并逐项检验选项。

做法：
1. 每个格子里找六边形外框：上、下两条水平边的端点和左右两个顶点直接从边框像素量出；
2. 删掉离六条边 <=2.6 像素的像素，剩下的连通块就是三个元素（圆与三角形贴边处会被削去一点，不影响判断）；
3. 分类：细长块（主轴/次轴方差比 >8）为短线，用 PCA 求方向角；其余块用最小二乘拟合圆，残差小的是圆，大的是三角形；
4. 圆：记录圆心最近的六边形边；三角形：记录离它最近的六边形顶点和它的质心；短线：记录方向角。
边编号（顺时针）：e0上边 e1右上边 e2右下边 e3下边 e4左下边 e5左上边。
顶点编号（顺时针）：v0左上 v1右上 v2右 v3右下 v4左下 v5左。
"""
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
EN = ['e0上边', 'e1右上边', 'e2右下边', 'e3下边', 'e4左下边', 'e5左上边']
VN = ['v0左上', 'v1右上', 'v2右', 'v3右下', 'v4左下', 'v5左']


def label(mask):
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
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and lab[ny, nx] == 0:
                                lab[ny, nx] = n
                                stack.append((ny, nx))
    return lab, n


def seg_dist(p, a_, b_):
    p, a_, b_ = map(np.asarray, (p, a_, b_))
    ab = b_ - a_
    t = np.clip(np.dot(p - a_, ab) / np.dot(ab, ab), 0, 1)
    return float(np.linalg.norm(p - (a_ + t * ab)))


def hexagon_vertices(sub):
    lab, n = label(sub)
    sizes = [(lab == i).sum() for i in range(1, n + 1)]
    m = lab == (int(np.argmax(sizes)) + 1)
    ys, xs = np.nonzero(m)
    ty, by, lx, rx = ys.min(), ys.max(), xs.min(), xs.max()
    top = np.nonzero(m[ty:ty + 2].any(axis=0))[0]
    bot = np.nonzero(m[by - 1:by + 1].any(axis=0))[0]
    ly = np.nonzero(m[:, lx:lx + 2].any(axis=1))[0].mean()
    ry = np.nonzero(m[:, rx - 1:rx + 1].any(axis=1))[0].mean()
    t = 1.0  # 线宽一半
    return [(top.min() + t, ty + t), (top.max() - t, ty + t), (rx - t, ry), (bot.max() - t, by - t),
            (bot.min() + t, by - t), (lx + t, ly)]


def circle_fit(pts):
    x, y = pts[:, 0], pts[:, 1]
    A = np.stack([x, y, np.ones_like(x)], 1)
    b = x ** 2 + y ** 2
    (D, E, F), *_ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy = D / 2, E / 2
    r = np.sqrt(F + cx ** 2 + cy ** 2)
    res = np.abs(np.hypot(x - cx, y - cy) - r).mean()
    return (cx, cy), r, res


def analyse(box):
    x0, y0, x1, y1 = box
    sub = dark[y0:y1, x0:x1]
    V = hexagon_vertices(sub)
    E = [(V[i], V[(i + 1) % 6]) for i in range(6)]
    rest = sub.copy()
    H, W = sub.shape
    for y in range(H):
        for x in range(W):
            if sub[y, x] and min(seg_dist((x, y), *e) for e in E) <= 2.6:
                rest[y, x] = False
    lab, n = label(rest)
    res = {'圆': [], '三角形': [], '短线': []}
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() < 15:          # 去掉残留碎点
            continue
        ys, xs = np.nonzero(m)
        pts = np.stack([xs, ys], 1).astype(float)
        c = pts.mean(0)
        ev, evec = np.linalg.eigh(np.cov((pts - c).T))
        if ev[1] / max(ev[0], 1e-6) > 8:
            vx, vy = evec[:, 1]
            ang = np.degrees(np.arctan2(-vy, vx)) % 180
            res['短线'].append(round(float(ang)))
            continue
        (cx, cy), r, err = circle_fit(pts)
        if err < 0.8 and 4 < r < 10:
            k = int(np.argmin([seg_dist((cx, cy), *e) for e in E]))
            res['圆'].append((EN[k], round(float(cx), 1), round(float(cy), 1)))
        else:
            k = int(np.argmin([np.min(np.hypot(xs - V[j][0], ys - V[j][1])) for j in range(6)]))
            res['三角形'].append((VN[k], round(float(c[0]), 1), round(float(c[1]), 1), int(m.sum())))
    return res


def line_kind(ang):
    if ang < 20 or ang > 160:
        return '—'
    return '/' if ang < 90 else '\\'


if __name__ == '__main__':
    R = {}
    for name, box in boxes.items():
        R[name] = analyse(box)
        r = R[name]
        print('%-3s 圆:%s  三角形:%s  短线:%s' % (name, r['圆'], r['三角形'],
                                              [(g, line_kind(g)) for g in r['短线']]))
    # 规律：圆每次逆时针移一条边；短线每次顺时针转60°（\ → / → — 循环）；三角形位置4图一循环（图5=图1，故问号=图2）
    print()
    print('圆所在边：', [R[k]['圆'][0][0] if R[k]['圆'] else '(与三角形相连)' for k in ['图1', '图2', '图3', '图4', '图5']])
    print('短线：', [line_kind(R[k]['短线'][0]) for k in ['图1', '图2', '图3', '图4', '图5']])
    print('三角形：', [R[k]['三角形'][0][:3] for k in ['图1', '图2', '图3', '图4', '图5']])
    exp_tri = R['图2']['三角形'][0]
    for o in 'ABCD':
        r = R[o]
        ok_c = bool(r['圆']) and r['圆'][0][0] == 'e5左上边'
        ok_l = bool(r['短线']) and line_kind(r['短线'][0]) == '—'
        t = r['三角形'][0]
        ok_t = t[0] == exp_tri[0] and abs(t[1] - exp_tri[1]) < 2.5 and abs(t[2] - exp_tri[2]) < 2.5
        print(o, '圆在左上边:', ok_c, ' 短线水平:', ok_l, ' 三角形同图2:', ok_t, ' => ', '符合' if ok_c and ok_l and ok_t else '不符')
