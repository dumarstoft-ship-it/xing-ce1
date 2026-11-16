"""Q47 九宫格：按像素采样读出每个小图的线段/弧，检验“前两图去同存异后上下翻转=第三图”。
第一行：圆心C、半径r，四个象限各可能有外凸弧o（大圆弧）和内凹弧i（以象限外角为圆心的弧），另有四条半径线。
第二行：4x4方格（5x5格点，间距15px）上的单位线段（横、竖、对角）。
第三行及选项：等距(六边形)格点 T,UL,UR,LL,LR,B,C 之间的连线。
"""
import math
import numpy as np
from PIL import Image

IMG = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s20_p12_i00.png'
a = np.array(Image.open(IMG).convert('L')).astype(float)


def dark_frac(pts, thr=140):
    hit = 0
    for x, y in pts:
        xi, yi = int(round(x)), int(round(y))
        win = a[yi - 1:yi + 2, xi - 1:xi + 2]
        hit += win.min() < thr
    return hit / len(pts)


def seg_pts(p, q, n=12, trim=0.2):
    return [(p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
            for t in np.linspace(trim, 1 - trim, n)]


# ---------- row 1: arcs ----------
def row1_features(cx, cy, r=33):
    feats = set()
    quad = {'TR': (1, -1), 'TL': (-1, -1), 'BL': (-1, 1), 'BR': (1, 1)}
    for q, (sx, sy) in quad.items():
        # convex arc: circle centre (cx,cy)
        pts = [(cx + sx * r * math.cos(t), cy + sy * r * math.sin(t)) for t in np.linspace(0.35, 1.22, 10)]
        if dark_frac(pts) > 0.8:
            feats.add(q + '_o')
        # concave arc: centre at the quadrant corner
        kx, ky = cx + sx * r, cy + sy * r
        pts = [(kx - sx * r * math.cos(t), ky - sy * r * math.sin(t)) for t in np.linspace(0.35, 1.22, 10)]
        if dark_frac(pts) > 0.8:
            feats.add(q + '_i')
    for name, (dx, dy) in {'C-T': (0, -1), 'C-B': (0, 1), 'C-L': (-1, 0), 'C-R': (1, 0)}.items():
        if dark_frac(seg_pts((cx, cy), (cx + dx * r, cy + dy * r))) > 0.8:
            feats.add(name)
    return feats


def flip_row1(fs):
    m = {'TL': 'BL', 'BL': 'TL', 'TR': 'BR', 'BR': 'TR'}
    out = set()
    for f in fs:
        if f.startswith('C-'):
            out.add({'C-T': 'C-B', 'C-B': 'C-T'}.get(f, f))
        else:
            q, k = f.split('_')
            out.add(m[q] + '_' + k)
    return out


# ---------- row 2: grid segments ----------
def row2_features(x0, y0=118, s=15):
    feats = set()
    for i in range(5):
        for j in range(5):
            for di, dj in ((1, 0), (0, 1), (1, 1), (1, -1)):
                i2, j2 = i + di, j + dj
                if not (0 <= i2 < 5 and 0 <= j2 < 5):
                    continue
                p = (x0 + i * s, y0 + j * s)
                q = (x0 + i2 * s, y0 + j2 * s)
                if dark_frac(seg_pts(p, q, 8, 0.25)) > 0.9:
                    feats.add(((i, j), (i2, j2)))
    return feats


def flip_row2(fs):
    out = set()
    for (p, q) in fs:
        p2, q2 = (p[0], 4 - p[1]), (q[0], 4 - q[1])
        out.add(tuple(sorted((p2, q2))))
    return out


def norm2(fs):
    return {tuple(sorted(e)) for e in fs}


# ---------- row 3 / options: hexagon lattice ----------
def lattice(cx, cy, h=33.0, w=29.0):
    return {'C': (cx, cy), 'T': (cx, cy - h), 'B': (cx, cy + h),
            'UL': (cx - w, cy - h / 2), 'LL': (cx - w, cy + h / 2),
            'UR': (cx + w, cy - h / 2), 'LR': (cx + w, cy + h / 2)}


def row3_features(cx, cy):
    P = lattice(cx, cy)
    names = list(P)
    feats = set()
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            u, v = names[i], names[j]
            d = math.dist(P[u], P[v])
            if d > 36:  # only neighbouring lattice points
                continue
            if dark_frac(seg_pts(P[u], P[v], 10, 0.2)) > 0.9:
                feats.add(frozenset((u, v)))
    return feats


def flip_row3(fs):
    m = {'T': 'B', 'B': 'T', 'UL': 'LL', 'LL': 'UL', 'UR': 'LR', 'LR': 'UR', 'C': 'C'}
    return {frozenset(m[x] for x in e) for e in fs}


def show(fs):
    return sorted('-'.join(sorted(e)) for e in fs)


def bbox_center(x0, y0, x1, y1):
    d = a[y0:y1, x0:x1] < 128
    ys, xs = np.nonzero(d)
    return (xs.min() + xs.max()) / 2 + x0, (ys.min() + ys.max()) / 2 + y0


if __name__ == '__main__':
    c11, c12, c13 = bbox_center(53, 6, 148, 95), bbox_center(152, 6, 247, 95), bbox_center(251, 6, 347, 95)
    r1 = [row1_features(*c11), row1_features(*c12), row1_features(*c13)]
    for k, f in enumerate(r1):
        print('row1 fig%d' % (k + 1), sorted(f))
    x1 = r1[0] ^ r1[1]
    print('row1: flipV(XOR) == fig3 ?', flip_row1(x1) == r1[2], '| plain XOR == fig3 ?', x1 == r1[2])

    r2 = [norm2(row2_features(x)) for x in (69, 170, 271)]
    for k, f in enumerate(r2):
        print('row2 fig%d: %d unit segments' % (k + 1, len(f)))
    x2 = r2[0] ^ r2[1]
    print('row2: flipV(XOR) == fig3 ?', flip_row2(x2) == r2[2], '| plain XOR == fig3 ?', x2 == r2[2])

    r3 = [row3_features(*bbox_center(53, 199, 148, 294)), row3_features(*bbox_center(152, 199, 247, 294))]
    for k, f in enumerate(r3):
        print('row3 fig%d' % (k + 1), show(f))
    target = flip_row3(r3[0] ^ r3[1])
    print('row3 predicted (flipV of XOR):', show(target))
    print('row3 plain XOR              :', show(r3[0] ^ r3[1]))
    opts = {'A': (10, 328, 101, 421), 'B': (106, 328, 198, 421), 'C': (203, 328, 294, 421), 'D': (299, 328, 391, 421)}
    for k, box in opts.items():
        f = row3_features(*bbox_center(*box))
        print('option', k, show(f), '-> match flipV(XOR):', f == target, '| match plain XOR:', f == (r3[0] ^ r3[1]))
