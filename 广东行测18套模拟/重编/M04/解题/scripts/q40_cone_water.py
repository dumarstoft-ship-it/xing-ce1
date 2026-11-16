"""第40题：高7米的圆锥底面朝上（尖端朝下）、恰好被淹没。水下部分是以尖端为顶点的相似小圆锥。
露出水面体积 ≥ 37/64 ⇔ 水下体积 ≤ 27/64 ⇔ 水下高度 ≤ 7×(27/64)^(1/3) = 7×3/4。
"""
from fractions import Fraction as F

H = F(7)
under_ratio = 1 - F(37, 64)
k = F(3, 4)
assert k ** 3 == under_ratio
h_under = H * k
drop = H - h_under
print("水下体积占比上限 =", under_ratio, "，相似比 =", k, "，水下高度上限 =", h_under, "米")
print("水位至少下降", drop, "=", float(drop), "米")
# 反向检验：下降1.75米时露出部分体积占比
print("下降1.75米时露出占比 =", 1 - (F(7) - F(7, 4)) ** 3 / H ** 3)
# 若误把“底面朝上”当成尖端朝上（露出部分为顶端小圆锥，(x/7)^3 = 37/64），会得到的数
print("误读（尖端朝上）时需露出高度 =", 7 * (37 / 64) ** (1 / 3), "米")
options = {"A": 1.54, "B": 1.75, "C": 2.10, "D": 3.00}
hits = [k_ for k_, v in options.items() if abs(v - float(drop)) < 1e-9]
assert hits == ["B"]
print("答案:", hits)
