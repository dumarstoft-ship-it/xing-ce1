"""M08 第38题：等边△ADE，B、C为AD、AE中点，BE、CD交于O，求四边形ABOC与其余部分面积比。坐标法+鞋带公式。"""
from fractions import Fraction as F
import math
def shoelace(pts):
    s = 0
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]+pts[:1]): s += x1*y2 - x2*y1
    return abs(s)/2
def solve(A, Dp, E):
    B = ((A[0]+Dp[0])/2, (A[1]+Dp[1])/2); C = ((A[0]+E[0])/2, (A[1]+E[1])/2)
    # O = 重心（两中线交点），用直线求交验证
    def inter(P1, P2, P3, P4):
        (x1, y1), (x2, y2), (x3, y3), (x4, y4) = P1, P2, P3, P4
        den = (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
        px = ((x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4))/den
        py = ((x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4))/den
        return (px, py)
    O = inter(B, E, C, Dp)
    tot = shoelace([A, Dp, E]); yel = shoelace([A, B, O, C])
    return yel, tot - yel
h = math.sqrt(3)
y, b = solve((0.0, h), (-1.0, 0.0), (1.0, 0.0))
print('等边三角形: 黄/蓝 =', y/b)
# 任意三角形同样成立（等边条件多余）
y2, b2 = solve((F(3), F(7)), (F(0), F(0)), (F(11), F(2)))
print('任意三角形: 黄/蓝 =', y2/b2)
assert abs(y/b - 0.5) < 1e-12 and y2/b2 == F(1, 2)
print('答案 A 1:2')
