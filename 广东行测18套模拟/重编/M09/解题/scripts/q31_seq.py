"""M09 第31题：3，9，18，30，45，（ ）  选项 A69 B66 C63 D60
核验：一级差 6,9,12,15 为公差3的等差数列，下一个差18；另：各项=3×三角形数(1,3,6,10,15,21)。"""
seq = [3, 9, 18, 30, 45]
opts = {'A': 69, 'B': 66, 'C': 63, 'D': 60}
d = [b - a for a, b in zip(seq, seq[1:])]
print('一级差:', d)
assert all(y - x == 3 for x, y in zip(d, d[1:]))
nxt = seq[-1] + d[-1] + 3
tri = [3 * n * (n + 1) // 2 for n in range(1, 7)]
print('3×三角形数:', tri)
assert tri[:5] == seq and tri[5] == nxt
ok = [k for k, v in opts.items() if v == nxt]
print('下一项', nxt, '对应选项', ok)
assert ok == ['C']
# 交叉验证：作商 3,2,5/3,3/2 即 (n+2)/n，下一个商 7/5，45×7/5=63
from fractions import Fraction as F
q = [F(b, a) for a, b in zip(seq, seq[1:])]
print('相邻项之商:', [str(x) for x in q])
assert q == [F(n + 2, n) for n in range(1, 5)] and seq[-1] * F(7, 5) == nxt
