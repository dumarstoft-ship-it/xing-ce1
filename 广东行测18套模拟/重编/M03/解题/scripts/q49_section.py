# 第49题：还原22块（16白6灰）组合体，按题图画法重渲染核对；再求过P、Q、R的截面
# 坐标：x向右、y向上、z向里（z越小越靠前）；斜二测 X=ox+u(x+kz), Y=oy-u(y+kz)
import numpy as np
from PIL import Image

IMG = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s18_p12_i00.png'
GRAY = {(1, 0, 1), (3, 0, 2), (0, 1, 1), (2, 1, 2), (1, 2, 2), (2, 2, 3)}
CUBES = [(1, 0, 0), (0, 0, 2), (0, 0, 3), (1, 0, 1), (1, 0, 2), (1, 0, 3), (2, 0, 1), (2, 0, 2), (2, 0, 3), (3, 0, 2),
         (0, 1, 1), (0, 1, 2), (0, 1, 3), (1, 1, 2), (1, 1, 3), (2, 1, 2), (2, 1, 3),
         (0, 2, 2), (0, 2, 3), (1, 2, 2), (1, 2, 3), (2, 2, 3)]
assert len(set(CUBES)) == 22 and len(GRAY) == 6
U, K, OX, OY, SC = 19.9, 0.40, 18.0, 112.5, 4


def render(cubes, colors, origin, size):
    W, H = size[0] * SC, size[1] * SC
    S = set(cubes)
    zbuf = np.full((H, W), np.inf); fid = np.full((H, W), -1, int); col = np.full((H, W), 255, np.uint8)
    ys, xs = np.mgrid[0:H, 0:W]; Xo = xs / SC; Yo = ys / SC
    faces = [(t, c) for c in S for t, n in (('F', (0, 0, -1)), ('T', (0, 1, 0)), ('R', (1, 0, 0)))
             if (c[0] + n[0], c[1] + n[1], c[2] + n[2]) not in S]
    for i, (t, (x, y, z)) in enumerate(faces):
        if t == 'F':
            a = (Xo - origin[0]) / U - K * z; b = (origin[1] - Yo) / U - K * z
            m = (a >= x) & (a <= x + 1) & (b >= y) & (b <= y + 1); d = np.full(a.shape, float(z))
        elif t == 'T':
            c = ((origin[1] - Yo) / U - (y + 1)) / K; a = (Xo - origin[0]) / U - K * c
            m = (a >= x) & (a <= x + 1) & (c >= z) & (c <= z + 1); d = c
        else:
            c = ((Xo - origin[0]) / U - (x + 1)) / K; b = (origin[1] - Yo) / U - K * c
            m = (b >= y) & (b <= y + 1) & (c >= z) & (c <= z + 1); d = c
        upd = m & (d < zbuf - 1e-9); zbuf[upd] = d[upd]; fid[upd] = i; col[upd] = colors[(x, y, z)]
    e = np.zeros((H, W), bool)
    e[:-1, :] |= fid[:-1, :] != fid[1:, :]; e[:, :-1] |= fid[:, :-1] != fid[:, 1:]
    return col, e, fid


def dilate(m, r):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out |= np.roll(np.roll(m, dy, 0), dx, 1)
    return out


colors = {c: (150 if c in GRAY else 255) for c in CUBES}
crop = (8, 30, 140, 112)        # 避开上方边框与字母P、Q
img = np.array(Image.open(IMG).convert('L'))
sub = img[crop[1]:crop[3], crop[0]:crop[2]]
o = np.array(Image.fromarray(sub).resize((sub.shape[1] * SC, sub.shape[0] * SC), Image.NEAREST)).astype(int)
col, e, fid = render(CUBES, colors, (OX - crop[0], OY - crop[1]), (crop[2] - crop[0], crop[3] - crop[1]))
interior = ~dilate(e, 8) & ~dilate(o < 90, 3) & (fid >= 0)
bad = (np.abs(o - col.astype(int)) > 50) & interior
print(f'渲染棱线无对应线条的像素：{(e & ~dilate(o < 90, 6)).sum()}；面内颜色不符像素：{bad.sum()}/{interior.sum()}')

# 隐藏位置检查：哪些块在画面上完全看不见
def hidden_positions():
    base = render(CUBES, colors, (OX, OY), (140, 125))[2]
    res = []
    for c in CUBES:
        rest = [d for d in CUBES if d != c]
        f2 = render(rest, colors, (OX, OY), (140, 125))[2]
        if ((base >= 0) != (f2 >= 0)).sum() == 0:
            # 去掉后轮廓不变，再比较可见面集合
            c1, e1, _ = render(CUBES, colors, (OX, OY), (140, 125)); c2, e2, _ = render(rest, colors, (OX, OY), (140, 125))
            if (e1 != e2).sum() == 0 and (c1 != c2).sum() == 0:
                res.append(c)
    return res


hid = hidden_positions()
print('画面上完全看不见的块：', hid, f'共{len(hid)}块；可见块{22 - len(hid)}块，6块灰色全部可见 -> 看不见的都是白色')

P, Q, R = np.array([0, 3, 4]), np.array([3, 3, 4]), np.array([3, 0, 1])
n = np.cross(Q - P, R - P); d = n @ P
print('截面法向量', n, '平面方程：', f'{n[1]}*y + {n[2]}*z = {d}', '即 z = y + 1')
print('被平面切过内部的块（z=y+1），按截面从上到下、从左到右排列（W白 G灰 _空）：')
for y in (2, 1, 0):
    row = ''
    for x in range(0, 4):
        c = (x, y, y + 1)
        row += ('G' if c in GRAY else 'W') if c in CUBES else '_'
    print('  ', row)
print('与A项（WWG / WWG / _GW）一致；B、C多出第4列，D中间行与下行不符。')
