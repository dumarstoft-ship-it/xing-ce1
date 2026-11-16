"""M05 第40题：转盘1~5等分，转3次，偶数区域次数多于奇数区域则获奖，求获奖概率。
枚举 5³=125 种等可能结果。
"""
from fractions import Fraction as F
from itertools import product
from math import comb

outcomes = list(product(range(1, 6), repeat=3))
win = [o for o in outcomes if sum(x % 2 == 0 for x in o) > sum(x % 2 == 1 for x in o)]
p = F(len(win), len(outcomes))
print("获奖结果数:", len(win), "/", len(outcomes), "=", p)

# 公式：P(偶)=2/5，至少2次偶数
q = F(2, 5)
formula = comb(3, 2) * q ** 2 * (1 - q) + q ** 3
print("公式:", formula)
assert p == formula == F(44, 125)
print("答案: A 44/125")
