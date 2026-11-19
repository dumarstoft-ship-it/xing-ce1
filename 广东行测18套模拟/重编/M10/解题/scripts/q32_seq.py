"""M10 第32题：92.46，84.42，76.38，68.34，（ ）  选项 A50.25 B53.26 C55.17 D56.30
原卷第27题（2023年县级卷第6页）已核对，数字与选项无误。"""
from fractions import Fraction as F
seq = ['92.46', '84.42', '76.38', '68.34']
opts = {'A': '50.25', 'B': '53.26', 'C': '55.17', 'D': '56.30'}
split = lambda s: tuple(int(x) for x in s.split('.'))
# 项内关系：整数部分 = 小数部分 × 2
for s in seq:
    i, f = split(s)
    assert i == 2 * f, s
ok = [k for k, s in opts.items() if split(s)[0] == 2 * split(s)[1]]
print('整数部分=2×小数部分 的选项：', ok)
assert ok == ['A']
# 项间关系：公差 −8.04 的等差数列，下一项 60.30，不在选项中
d = [F(b) - F(a) for a, b in zip(seq, seq[1:])]
assert len(set(d)) == 1
nxt = F(seq[-1]) + d[0]
print('等差续写：公差', float(d[0]), '下一项', float(nxt), '在选项中？', any(F(v) == nxt for v in opts.values()))
# 易错核对：只续写小数部分（46、42、38、34 → 30），选项中小数部分为30的只有D
print('小数部分为30的选项：', [k for k, s in opts.items() if split(s)[1] == 30])
assert [k for k, s in opts.items() if split(s)[1] == 30] == ['D']
