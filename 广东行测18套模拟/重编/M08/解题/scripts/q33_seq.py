"""M08 第33题：16/3，8，4，6，3，9/2，（ ）  隔项等比（公比3/4）；作商得 3/2、1/2 交替"""
from fractions import Fraction as F
seq = [F(16, 3), F(8), F(4), F(6), F(3), F(9, 2)]
opts = {'A': F(16), 'B': F(12), 'C': F(15, 4), 'D': F(9, 4)}
ratios = [seq[i+1]/seq[i] for i in range(len(seq)-1)]
print('相邻作商:', [str(r) for r in ratios])
gap = [seq[i+2]/seq[i] for i in range(len(seq)-2)]
print('隔项作商:', [str(r) for r in gap])
assert all(g == F(3, 4) for g in gap)
pred = seq[-2] * F(3, 4)
ans = [k for k, v in opts.items() if v == pred]
print('预测', pred, '答案', ans)
assert ans == ['D']
