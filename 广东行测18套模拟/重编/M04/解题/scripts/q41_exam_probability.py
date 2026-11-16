"""第41题：4人笔试，首考合格概率0.8；未合格者可补考一次，补考合格概率0.4；
若首考合格人数不足总人数一半（即少于2人），取消补考。求恰好3人最终合格的概率。
逐人枚举全部结果（首考是否合格 × 补考是否合格），精确求和。
"""
from fractions import Fraction as F
from itertools import product

p1, p2 = F(4, 5), F(2, 5)
N = 4
total = F(0)
by_first = {}
for first in product((True, False), repeat=N):
    pf = F(1)
    for f in first:
        pf *= p1 if f else 1 - p1
    k = sum(first)
    failed = N - k
    if 2 * k < N:  # 不足一半，取消补考
        if k == 3:
            total += pf
        continue
    for second in product((True, False), repeat=failed):
        ps = F(1)
        for s in second:
            ps *= p2 if s else 1 - p2
        if k + sum(second) == 3:
            total += pf * ps
            by_first[k] = by_first.get(k, 0) + pf * ps
print("按首考合格人数拆分:", {k: (str(v), float(v)) for k, v in by_first.items()})
print("P(恰3人合格) =", total, "≈", float(total))
# 对照：若误把首考2人合格也视为取消补考
wrong = by_first.get(3, 0)
print("只算“首考3人合格”一种情形 =", float(wrong))
options = {"A": 0.20, "B": 0.25, "C": 0.28, "D": 0.32}
best = min(options, key=lambda k: abs(options[k] - float(total)))
print("最接近选项:", best)
assert best == "D"
