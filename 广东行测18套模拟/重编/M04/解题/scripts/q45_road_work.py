"""第45题：甲乙合作20天完成，甲效率=5×乙。完成80%时乙撤出、丙加入，最终比原计划提前1天。
设乙效率1，甲5，总量(5+1)×20=120。求丙单独完成天数。
"""
from fractions import Fraction as F

b, a = F(1), F(5)
total = (a + b) * 20
t1 = total * F(8, 10) / (a + b)
rest_days = 20 - 1 - t1
rest_work = total * F(2, 10)
c = rest_work / rest_days - a
print("总量", total, "，前80%用时", t1, "天，剩余", rest_work, "用时", rest_days, "天")
print("丙效率 =", c, "，丙单独需", total / c, "天")
options = {"A": 30, "B": 24, "C": 35, "D": 40}
hits = [k for k, v in options.items() if v == total / c]
assert hits == ["D"]
print("答案:", hits)
