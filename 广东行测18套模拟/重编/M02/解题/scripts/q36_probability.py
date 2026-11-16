"""第36题：10个面包（红豆4、肉松3、全麦3），不放回抽3个，恰好2红豆1肉松的概率。
选项 A 9/50  B 3/20  C 7/40  D 11/60

核验：组合公式 + 对 10×9×8 种有序抽法全部枚举。
"""
from fractions import Fraction as F
from itertools import permutations
from math import comb

breads = ["红豆"] * 4 + ["肉松"] * 3 + ["全麦"] * 3
options = {"A": F(9, 50), "B": F(3, 20), "C": F(7, 40), "D": F(11, 60)}

p_formula = F(comb(4, 2) * comb(3, 1), comb(10, 3))
print("组合公式 C(4,2)C(3,1)/C(10,3) =", comb(4, 2) * comb(3, 1), "/", comb(10, 3), "=", p_formula)

total = good = 0
for draw in permutations(range(10), 3):
    total += 1
    kinds = [breads[i] for i in draw]
    if kinds.count("红豆") == 2 and kinds.count("肉松") == 1:
        good += 1
p_enum = F(good, total)
print("有序枚举", good, "/", total, "=", p_enum)
assert p_enum == p_formula
print("对应选项:", [k for k, v in options.items() if v == p_enum])
