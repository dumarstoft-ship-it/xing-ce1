"""S02 第38题：甲300千米/时、乙200千米/时，同程同时出发，快车少用40分钟，求路程。 选项 A200 B300 C400 D500"""
from fractions import Fraction as F
x = F(40, 60) / (F(1, 200) - F(1, 300))
print('路程', x)
assert x == 400
for k, v in {'A': 200, 'B': 300, 'C': 400, 'D': 500}.items():
    print(k, v, '时间差', (F(v, 200) - F(v, 300)) * 60, '分钟')
