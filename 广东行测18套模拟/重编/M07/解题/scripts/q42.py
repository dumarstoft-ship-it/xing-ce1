# 第42题：圆台杯 上口直径8 下底直径6 高10；圆柱桶 直径20 高18.5；最少几杯灌满
from fractions import Fraction as F
from math import ceil
R, r, h = 4, 3, 10
V_cup = F(1, 3) * h * (R * R + R * r + r * r)        # 单位：π cm^3 → 370/3 π
V_bucket = F(10) ** 2 * F(37, 2)                      # 1850 π
n = V_bucket / V_cup
print("杯容积", V_cup, "π；桶容积", V_bucket, "π；比值", n, "→ 最少", ceil(n), "杯")
assert n == 15
# 易错：把圆台按平均半径3.5的圆柱算 → 122.5π → 1850/122.5≈15.1 → 16杯（C）
wrong = V_bucket / (F(7, 2) ** 2 * h)
print("按平均半径圆柱算：", float(wrong), "→", ceil(wrong))
# 按上口半径4的圆柱算 → 160π → 11.6 → 12；按下底半径3 → 90π → 20.6 → 21
print("上口圆柱", float(V_bucket / (16 * h)), "下底圆柱", float(V_bucket / (9 * h)))
