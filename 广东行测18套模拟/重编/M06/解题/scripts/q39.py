# 第39题：加150ml后占容积4/9，再加100ml后占2/3，求初始体积。
from fractions import Fraction as F
V = F(100) / (F(2, 3) - F(4, 9))
x = F(4, 9) * V - 150
print("容积", V, "初始", x)
assert x == 50 and F(2, 3) * V - 250 == 50
# 枚举整数ml验证唯一
sols = [(v, x0) for v in range(1, 5000) for x0 in [v * 4 / 9 - 150] if x0 >= 0 and abs((x0 + 250) - v * 2 / 3) < 1e-9]
print("枚举(容积,初始):", sols)
print("答案: A")
