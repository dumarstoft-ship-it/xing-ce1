"""Q46 一组图：检验“每图5个封闭区域，且其中有一个区域与图形外轮廓形状相同（相似）”。
1) 封闭区域数：对白色像素做连通域标记，去掉与边框相连的背景，剩下的即封闭区域。
2) 形状相似：把整个图形（外轮廓内部全部填满）作为“外轮廓形状”，对每个区域算Hu不变矩
   （对平移、缩放、旋转、翻转不变），并用轮廓追踪+Douglas-Peucker数出多边形边数。
"""
import math
from collections import deque
import numpy as np
from PIL import Image

IMG = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s20_p11_i00.png'
a = np.array(Image.open(IMG).convert('L'))
TOP = [3, 102, 200, 299, 398, 496, 595]
BOT = [104, 202, 301, 400, 499]
CROPS = [('图%d' % (i + 1), 10, 104, TOP[i] + 5, TOP[i + 1] - 3) for i in range(5)] + \
        [('选项' + 'ABCD'[i], 141, 236, BOT[i] + 5, BOT[i + 1] - 3) for i in range(4)]


def label_white(arr, thr=160):
    white = arr >= thr
    H, W = white.shape
    lab = -np.ones((H, W), int)
    comps = []
    for y in range(H):
        for x in range(W):
            if white[y, x] and lab[y, x] < 0:
                q = deque([(y, x)]); idx = len(comps); lab[y, x] = idx; n = 0; touch = False
                while q:
                    cy, cx = q.popleft(); n += 1
                    if cy in (0, H - 1) or cx in (0, W - 1):
                        touch = True
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < H and 0 <= nx < W and white[ny, nx] and lab[ny, nx] < 0:
                            lab[ny, nx] = idx; q.append((ny, nx))
                comps.append({'n': n, 'touch': touch})
    return lab, comps


def hu_feat(mask):
    ys, xs = np.nonzero(mask)
    x = xs.astype(float); y = ys.astype(float)
    m00 = len(x); xb, yb = x.mean(), y.mean()
    eta = lambda p, q: (((x - xb) ** p) * ((y - yb) ** q)).sum() / m00 ** (1 + (p + q) / 2)
    n20, n02, n11 = eta(2, 0), eta(0, 2), eta(1, 1)
    n30, n03, n21, n12 = eta(3, 0), eta(0, 3), eta(2, 1), eta(1, 2)
    h1 = n20 + n02
    h2 = (n20 - n02) ** 2 + 4 * n11 ** 2
    h3 = (n30 - 3 * n12) ** 2 + (3 * n21 - n03) ** 2
    h4 = (n30 + n12) ** 2 + (n21 + n03) ** 2
    return np.array([h1, math.sqrt(h2), h3 ** (1 / 3), h4 ** (1 / 3)])


def trace(mask):
    """Moore-neighbour boundary tracing; returns ordered boundary pixels (x,y)."""
    H, W = mask.shape
    pad = np.zeros((H + 2, W + 2), bool); pad[1:-1, 1:-1] = mask
    ys, xs = np.nonzero(pad)
    k = np.lexsort((xs, ys))[0]
    s = (ys[k], xs[k])
    nb = [(0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1)]  # W,NW,N,NE,E,SE,S,SW (clockwise)
    c, back = s, 0  # came from the west
    out = [s]
    for _ in range(100000):
        found = None
        for i in range(1, 9):
            d = (back + i) % 8
            p = (c[0] + nb[d][0], c[1] + nb[d][1])
            if pad[p]:
                found = (p, d); break
        if found is None:
            break
        p, d = found
        prev = (d - 1) % 8
        q = (c[0] + nb[prev][0], c[1] + nb[prev][1])
        back = nb.index((q[0] - p[0], q[1] - p[1]))
        c = p
        if c == s and len(out) > 2:
            break
        out.append(c)
    return [(x - 1, y - 1) for y, x in out]


def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    a_, b_ = np.array(pts[0], float), np.array(pts[-1], float)
    ab = b_ - a_; L = np.hypot(*ab)
    d = [abs(ab[0] * (p[1] - a_[1]) - ab[1] * (p[0] - a_[0])) / L if L else np.hypot(p[0] - a_[0], p[1] - a_[1]) for p in pts]
    i = int(np.argmax(d))
    if d[i] > eps:
        return rdp(pts[:i + 1], eps)[:-1] + rdp(pts[i:], eps)
    return [pts[0], pts[-1]]


def n_vertices(mask, eps=2.2):
    b = trace(mask)
    P = np.array(b, float)
    i0 = int(np.argmax(((P - P.mean(0)) ** 2).sum(1)))
    b = b[i0:] + b[:i0]
    i1 = int(np.argmax(((np.array(b, float) - np.array(b[0], float)) ** 2).sum(1)))
    poly = rdp(b[:i1 + 1], eps)[:-1] + rdp(b[i1:] + [b[0]], eps)[:-1]
    changed = True
    while changed and len(poly) > 3:  # merge nearly collinear / very close vertices
        changed = False
        for k in range(len(poly)):
            p0, p1, p2 = (np.array(poly[k - 1], float), np.array(poly[k], float), np.array(poly[(k + 1) % len(poly)], float))
            v1, v2 = p1 - p0, p2 - p1
            ang = abs(math.degrees(math.atan2(v1[0] * v2[1] - v1[1] * v2[0], v1 @ v2)))
            if ang < 15 or np.hypot(*v1) < 3:
                poly.pop(k); changed = True; break
    return len(poly)


if __name__ == '__main__':
    for name, y0, y1, x0, x1 in CROPS:
        c = a[y0:y1, x0:x1]
        lab, comps = label_white(c)
        bg = [k for k, cm in enumerate(comps) if cm['touch']]
        outer = ~np.isin(lab, bg)
        fo = hu_feat(outer)
        nv_outer = n_vertices(outer)
        regs = []
        for k, cm in enumerate(comps):
            if cm['touch'] or cm['n'] < 15:
                continue
            m = lab == k
            d = np.abs(hu_feat(m) - fo).sum() / np.abs(fo).sum()
            regs.append((d, n_vertices(m), cm['n']))
        regs.sort()
        best = regs[0]
        print('%s: 封闭区域=%d, 外轮廓边数=%d, 各区域边数=%s, 与外轮廓最相似区域: Hu距离=%.3f 边数=%d (次相似 %.3f)'
              % (name, len(regs), nv_outer, sorted(r[1] for r in regs), best[0], best[1], regs[1][0]))
