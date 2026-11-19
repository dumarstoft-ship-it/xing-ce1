"""M10 第47题（GD2018-Q039）：数交点。

各图的线段端点由4倍放大图读出（单位：放大图像素；斜线端点落在边上的，按所在边的直线方程取准）。
交点 = 两条及以上线段相交或相接的点（角点、T形点、十字点都算），按 10 像素合并。
同时给出线条数（共线的边与延长段算一条），说明线条数没有规律（7、5、7、5）。
"""
from itertools import combinations

def on_line(p, a, b, t):
    """在直线 ab 上取纵坐标(t='y')或横坐标(t='x')给定的点"""
    (x1, y1), (x2, y2) = a, b
    if t[0] == 'y':
        y = t[1]; return (x1 + (y - y1) * (x2 - x1) / (y2 - y1), y)
    x = t[1]; return (x, y1 + (x - x1) * (y2 - y1) / (x2 - x1))

def inter(s1, s2, eps=1e-9):
    (x1, y1), (x2, y2) = s1; (x3, y3), (x4, y4) = s2
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(d) < eps:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / d
    tol = 0.02
    if -tol <= t <= 1 + tol and -tol <= u <= 1 + tol:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None

def count(segs, merge=10):
    pts = []
    for s1, s2 in combinations(segs, 2):
        p = inter(s1, s2)
        if p:
            pts.append(p)
    uniq = []
    for p in pts:
        if not any(abs(p[0] - q[0]) < merge and abs(p[1] - q[1]) < merge for q in uniq):
            uniq.append(p)
    return uniq

F = {}
# 图1：正方形 + 上边一点P向左下角、右下角连线 + 斜线上一点J向底边的竖线
TL, TR, BR, BL, P = (108, 130), (660, 130), (660, 680), (108, 680), (245, 130)
J = on_line(None, P, BR, ('x', 490)); K = (490, 680)
F['图1'] = [(TL, TR), (TR, BR), (BL, BR), (TL, BL), (P, BL), (P, BR), (J, K)]
# 图2：长方形，底边向左延长到L，L向右边上的S连斜线
TL, TR, BR, BL, L, S = (365, 120), (635, 120), (635, 665), (365, 665), (85, 665), (635, 245)
F['图2'] = [(TL, TR), (TR, BR), (L, BR), (TL, BL), (L, S)]
# 图3：上边P1P2P3、下边Q1Q2Q3，五条连线
P1, P2, P3, Q1, Q2, Q3 = (180, 135), (420, 135), (670, 135), (45, 688), (430, 688), (580, 688)
F['图3'] = [(P1, P3), (Q1, Q3), (P1, Q2), (Q1, P2), (P2, Q2), (P3, Q2), (P3, Q3)]
# 图4：上短横、右竖线、长斜线、底边、左下小斜线（小斜线下端即底边左端）
A, B, V, W, E = (215, 148), (408, 148), (408, 688), (318, 688), (605, 688)
F['图4'] = [(A, B), (B, V), (W, E), (A, E), (W, (408, 585))]
# A项
TL, TR, BL, M, N, Bb = (228, 122), (540, 122), (228, 685), (228, 412), (480, 412), (405, 685)
F['A'] = [(TL, BL), (TL, TR), (TR, BL), (M, N), (N, Bb), (BL, Bb)]
# B项：三角形 + 右边上一点到底边的线 + 左下角到这条线的线
Ap, BL, BR = (378, 120), (88, 670), (665, 670)
R1 = on_line(None, Ap, BR, ('y', 252)); Bm = (530, 670); Jb = on_line(None, R1, Bm, ('y', 400))
F['B'] = [(Ap, BL), (Ap, BR), (BL, BR), (R1, Bm), (BL, Jb)]
# C项
TL, TR, BR, E, Fp = (165, 135), (612, 135), (612, 680), (612, 415), (205, 545)
F['C'] = [(TL, TR), (TR, BR), (TL, BR), (E, Fp), (Fp, BR)]
# D项
BL, Top, Vb, BR = (120, 672), (462, 115), (462, 672), (605, 672)
G = on_line(None, BL, Top, ('y', 318))
F['D'] = [(BL, Top), (Top, Vb), (BL, BR), (G, BR)]

for k, segs in F.items():
    pts = count(segs)
    print(f'{k}: 交点 {len(pts)} 个；线条 {len(segs)} 条')
