# 第44题：矩形四周与两条对角线上架木桩，间距相同；相邻两边（含顶点）分别7根、9根
from fractions import Fraction as F
a, b = 6, 8            # 两边各有6段、8段（单位：间距d）
diag = (a * a + b * b) ** 0.5
assert diag == 10
pts = set()
# 四周
for i in range(a + 1):
    pts.add((F(0), F(i))); pts.add((F(b), F(i)))
for j in range(b + 1):
    pts.add((F(j), F(0))); pts.add((F(j), F(a)))
perim = len(pts)
# 两条对角线，从顶点起每隔1个间距（对角线长10个间距）
for k in range(11):
    t = F(k, 10)
    pts.add((b * t, a * t))
    pts.add((b * t, a - a * t))
print("四周木桩", perim, "总木桩", len(pts))
assert len(pts) == 45
print("忘记扣除对角线交点重合：", perim + 2 * 9, "；每条对角线按10根算：", perim + 20, "；按10根再扣交点：", perim + 19)
