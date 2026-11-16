"""第38题：甲先做2天，乙加入合做10天完成240个：12a+10b=240；
乙先做5天，甲再单独做18天完成：5b+18a=240。求 240/a − 240/b。
另检验“乙做5天后甲加入合做18天”的读法会得出负效率，从而排除。
"""
from fractions import Fraction as F

def solve(a1, b1, c1, a2, b2, c2):
    det = a1 * b2 - a2 * b1
    return F(c1 * b2 - c2 * b1, det), F(a1 * c2 - a2 * c1, det)

a, b = solve(12, 10, 240, 18, 5, 240)
print("甲效率 a =", a, "个/天，乙效率 b =", b, "个/天")
ta, tb = 240 / a, 240 / b
print("甲单独", ta, "天，乙单独", tb, "天，差", ta - tb)
a2, b2 = solve(12, 10, 240, 18, 23, 240)
print("另一读法（乙共做23天）：a =", a2, "b =", b2, "（出现负数，读法不成立）")
options = {"A": 1, "B": 2, "C": 3, "D": 4}
hits = [k for k, v in options.items() if v == ta - tb]
assert hits == ["D"]
print("答案:", hits)
