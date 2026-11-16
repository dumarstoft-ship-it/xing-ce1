"""第42题：火车完全通过600米隧道用55秒；隧道顶部固定灯垂直照射火车25秒。求车长。
选项 A300 B400 C500 D600

关系：完全通过隧道走 (600+L)，灯照射火车的时间对应火车走过自身长度 L。
核验：逐一代入选项，看两种情形算出的车速是否一致；再枚举 1~2000 米确认唯一。
"""
from fractions import Fraction as F

options = {"A": 300, "B": 400, "C": 500, "D": 600}
for k, L in options.items():
    v1 = F(600 + L, 55)
    v2 = F(L, 25)
    print(k, L, "隧道得车速", float(v1), "灯照得车速", float(v2), "一致" if v1 == v2 else "")
print("1~2000 内满足的车长:", [L for L in range(1, 2001) if F(600 + L, 55) == F(L, 25)])
