"""M11 第33题：−3，8，2，18，22，（ ）  选项 A43 B58 C60 D76
规律：a(n)=a(n−1)+2a(n−2)：2=8+2×(−3)，18=2+2×8，22=18+2×2 → 22+2×18=58。"""
import itertools
seq = [-3, 8, 2, 18, 22]
opts = {'A': 43, 'B': 58, 'C': 60, 'D': 76}
assert all(seq[i] == seq[i - 1] + 2 * seq[i - 2] for i in range(2, 5))
nxt = seq[-1] + 2 * seq[-2]
print('下一项', nxt)
# 穷举线性二阶递推 a(n)=x·a(n−1)+y·a(n−2)+z（系数−4…4）
hits = {}
R = range(-4, 5)
for x, y, z in itertools.product(R, R, R):
    if all(seq[i] == x * seq[i - 1] + y * seq[i - 2] + z for i in range(2, 5)):
        hits.setdefault(x * seq[-1] + y * seq[-2] + z, []).append((x, y, z))
print('拟合前五项的线性二阶递推：', hits)
assert list(hits) == [58]
print('答案：', [k for k, v in opts.items() if v == nxt])
