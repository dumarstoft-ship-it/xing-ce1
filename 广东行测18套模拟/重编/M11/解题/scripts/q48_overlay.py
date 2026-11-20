"""M11 第48题（GD2014-XJ-Q059）：图2上下翻转后与图1叠加，“去异求同”得图3。

坐标读自题图第二组3倍放大图（单位：放大图像素）。把图5沿水平中线翻转、平移到图4的位置，
找两图重合的线段与圆；再给出两组各图的直线条数（备查：两组都是10、12条，只是巧合，见解析）。
"""
import math

def flip_shift(p, yc, dx):
    return (p[0] + dx, 2 * yc - p[1])

def overlap(s1, s2, ang_tol=4, dist_tol=12):   # 放大3倍图上12像素≈原图4像素的读数误差
    seglen = lambda s: math.dist(s[0], s[1])
    if seglen(s1) < seglen(s2):          # 以较长的一段为基准，量较短一段两端到它的距离
        s1, s2 = s2, s1
    (x1, y1), (x2, y2) = s1; (x3, y3), (x4, y4) = s2
    a1 = math.degrees(math.atan2(y2 - y1, x2 - x1)) % 180
    a2 = math.degrees(math.atan2(y4 - y3, x4 - x3)) % 180
    if min(abs(a1 - a2), 180 - abs(a1 - a2)) > ang_tol:
        return None
    L = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / L, (y2 - y1) / L
    d = lambda x, y: abs((x - x1) * uy - (y - y1) * ux)
    if d(x3, y3) > dist_tol or d(x4, y4) > dist_tol:
        return None
    t = lambda x, y: (x - x1) * ux + (y - y1) * uy
    lo, hi = max(0, min(t(x3, y3), t(x4, y4))), min(L, max(t(x3, y3), t(x4, y4)))
    if hi - lo < 15:
        return None
    return ((round(x1 + lo * ux), round(y1 + lo * uy)), (round(x1 + hi * ux), round(y1 + hi * uy)))

# 图4：正五边形+五角星+圆
T4, L4, R4, BL4, BR4 = (322, 72), (125, 215), (520, 215), (205, 445), (440, 445)
fig4 = [(T4, L4), (L4, BL4), (BL4, BR4), (BR4, R4), (R4, T4),           # 五边形
        (T4, BL4), (T4, BR4), (L4, R4), (L4, BR4), (R4, BL4)]           # 五角星
circle4 = ((325, 282), 57)
# 图5：外轮廓、大三角形、顶部短线、底边、底部V形、圆
T, L1, L2, B, R2, R1 = (895, 72), (705, 215), (705, 310), (895, 460), (1085, 310), (1085, 215)
fig5 = [(T, L1), (L1, L2), (L2, B), (B, R2), (R2, R1), (R1, T),
        (T, L2), (T, R2), ((855, 128), (935, 128)), (L2, R2), ((855, 310), B), ((935, 310), B)]
circle5 = ((895, 245), 62)
yc, dx = (72 + 460) / 2, 322 - 895
f5 = [(flip_shift(a, yc, dx), flip_shift(b, yc, dx)) for a, b in fig5]
c5 = (flip_shift(circle5[0], yc, dx), circle5[1])
common = []
for s in f5:
    for t in fig4:
        o = overlap(s, t)
        if o:
            common.append(o)
print('图5翻转后与图4重合的线段：')
for c in common:
    print('  ', c)
print('圆心距离', round(math.dist(c5[0], circle4[0]), 1), '半径', c5[1], circle4[1])
print('→ 重合部分：顶点向左右两点的两条边、两点间的横线、顶点下来的两条短斜线（止于横线）、横线下的圆，即D项。')
print('直线条数：第一组 10、12、6；第二组 10、12，选项 A 6、B 12、C 10、D 5（第二组各图另有1个圆）')
