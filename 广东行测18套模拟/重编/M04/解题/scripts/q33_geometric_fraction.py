"""第33题：9/10，3/5，2/5，4/15，（ ），16/135
相邻两项之比恒为2/3（等比数列）。逐个代入选项检验空位前后两个比值。
"""
from fractions import Fraction as F

seq = [F(9, 10), F(3, 5), F(2, 5), F(4, 15), None, F(16, 135)]
ratios = [seq[i + 1] / seq[i] for i in range(3)]
print("已知比值:", ratios)
options = {"A": F(7, 45), "B": F(8, 45), "C": F(7, 60), "D": F(2, 15)}
hits = []
for k, v in options.items():
    r1 = v / seq[3]
    r2 = seq[5] / v
    ok = r1 == F(2, 3) and r2 == F(2, 3)
    print(k, v, "前比", r1, "后比", r2, "OK" if ok else "")
    if ok:
        hits.append(k)
assert hits == ["B"]
print("答案:", hits)
