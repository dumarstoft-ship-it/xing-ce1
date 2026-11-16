"""M05 第41题：一、二车间合作20天完成；一车间先做6天、二车间再做8天，剩66%；
一车间每天比二车间多150个，求二车间单独完成天数。
设总量为1，效率 a、b：a+b=1/20，6a+8b=1-0.66。再用零件个数枚举核对。
"""
from fractions import Fraction as F

s = F(1, 20)
done = 1 - F(66, 100)
# 6a+8b = done, a+b = s  =>  2b = done - 6s
b = (done - 6 * s) / 2
a = s - b
print("效率(占总量/天): 一车间", a, "二车间", b)
assert (a, b) == (F(3, 100), F(1, 50))
days_b = 1 / b
print("二车间单独需要", days_b, "天")
assert days_b == 50

# 用"每天多150个"求总量，并枚举整数效率核对
total = 150 / (a - b)
print("零件总数:", total, "一车间每天", a * total, "二车间每天", b * total)
sols = []
for bb in range(1, 2001):
    aa = bb + 150
    T = 20 * (aa + bb)
    if 100 * (6 * aa + 8 * bb) == 34 * T:
        sols.append((aa, bb, T, F(T, bb)))
print("枚举(一车间日产,二车间日产,总量,二车间天数):", sols)
assert len(sols) == 1 and sols[0][3] == 50
print("答案: D 50")
