"""第43题：按x%利润率定价再打9折，利润率比x%低12个百分点：0.9(1+x%) − 1 = x% − 12%。
前50件每件获利 进价×x%，其余100件每件获利x元，总利润6000元，求进价。
先精确解x，再逐个代入选项检验总利润。
"""
from fractions import Fraction as F

# 0.9(1+t) - 1 = t - 0.12, t = x/100
t = (F(9, 10) - 1 + F(12, 100)) / (1 - F(9, 10))
x = t * 100
print("x% =", t, "→ x =", x)
assert 0.9 * (1 + float(t)) - 1 - (float(t) - 0.12) < 1e-12
options = {"A": 400, "B": 500, "C": 600, "D": 700}
hits = []
for k, cost in options.items():
    profit = 50 * cost * t + 100 * x
    print(k, "进价", cost, "总利润", profit)
    if profit == 6000:
        hits.append(k)
assert hits == ["A"]
print("答案:", hits)
