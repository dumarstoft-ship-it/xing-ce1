"""M09 第34题：1/8，1/6，3/16，1/5，（ ）  选项 A1/3 B2/9 C5/18 D5/24
核验：反约分 1/8,2/12,3/16,4/20，分子1,2,3,4，分母8,12,16,20（公差4），下一项5/24。"""
from fractions import Fraction as F
seq = [F(1, 8), F(1, 6), F(3, 16), F(1, 5)]
opts = {'A': F(1, 3), 'B': F(2, 9), 'C': F(5, 18), 'D': F(5, 24)}
gen = [F(n, 4 * n + 4) for n in range(1, 6)]
print('n/(4n+4):', [f'{n}/{4*n+4}' for n in range(1, 6)], [str(x) for x in gen])
assert gen[:4] == seq
ok = [k for k, v in opts.items() if v == gen[4]]
print('第5项', gen[4], '对应选项', ok)
assert ok == ['D']
# 小数检验：数列单调递增且增幅递减
print('小数值:', [round(float(x), 4) for x in seq + [gen[4]]])
