"""M05 第42题：20%甲 + 50%乙 → 32%丙，甲比乙多60克，求丙中溶质质量。
十字交叉/方程求解，再枚举整数质量确认唯一。
"""
from fractions import Fraction as F

# 十字交叉：甲:乙 = (50-32):(32-20) = 18:12 = 3:2
r = F(50 - 32, 32 - 20)
print("甲:乙 =", r)
y = F(60) / (r - 1)
x = y + 60
print("甲", x, "克，乙", y, "克，丙", x + y, "克")
solute = x * F(20, 100) + y * F(50, 100)
print("溶质:", solute, "；校验浓度:", solute / (x + y))
assert solute == 96 and solute / (x + y) == F(32, 100)

sols = [(xx, xx - 60) for xx in range(61, 10001)
        if F(20 * xx + 50 * (xx - 60), 100) == F(32, 100) * (2 * xx - 60)]
print("枚举整数解:", sols)
assert sols == [(180, 120)]
print("答案: A 96（C项300是丙溶液的质量）")
