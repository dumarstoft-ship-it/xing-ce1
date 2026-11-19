"""M10 第33题：1，2，3，10，39，（ ）  选项 A157 B257 C390 D490
规律：a(n)=a(n−2)×[a(n−1)+a(n−2)]，即 3=1×(2+1)、10=2×(3+2)、39=3×(10+3)。"""
import itertools
seq = [1, 2, 3, 10, 39]
opts = {'A': 157, 'B': 257, 'C': 390, 'D': 490}
rule = lambda p, q: p * (q + p)          # p=a(n−2), q=a(n−1)
assert all(seq[i] == rule(seq[i - 2], seq[i - 1]) for i in range(2, 5))
nxt = rule(seq[-2], seq[-1])
print('下一项', nxt, '=10×(39+10)')
assert nxt == 490
# 穷举同类二阶递推 a(n)=x·a(n−1)·a(n−2)+y·a(n−1)+z·a(n−2)+u·a(n−2)²+w (系数−3…3)，
# 看能拟合前五项的规律给出哪些选项
hits = {}
R = range(-3, 4)
for x, y, z, u, w in itertools.product(R, R, R, R, R):
    f = lambda p, q: x * p * q + y * q + z * p + u * p * p + w
    if all(seq[i] == f(seq[i - 2], seq[i - 1]) for i in range(2, 5)):
        v = f(seq[-2], seq[-1])
        hits.setdefault(v, []).append((x, y, z, u, w))
print('拟合前五项的同类递推给出的下一项：', {k: len(v) for k, v in hits.items()})
print('落在选项上的：', {k: v for k, v in opts.items() if v in hits})
