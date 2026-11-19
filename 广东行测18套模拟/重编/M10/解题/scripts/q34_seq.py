"""M10 第34题：6/6，4/6，3/6，2/5，（ ）  选项 A1/3 B1/2 C2/5 D1/6
原卷（2021年乡镇卷第35题，第4页）分数为公式图，已放大核对。"""
from fractions import Fraction as F
seq = [F(6, 6), F(4, 6), F(3, 6), F(2, 5)]
opts = {'A': F(1, 3), 'B': F(1, 2), 'C': F(2, 5), 'D': F(1, 6)}
# 化简后为 1、2/3、1/2、2/5，即 2/2、2/3、2/4、2/5（分子统一为2）
assert seq == [F(2, n) for n in range(2, 6)]
nxt = F(2, 6)
# 等价看法：倒数 1、1.5、2、2.5 公差0.5
inv = [1 / x for x in seq]
assert len({b - a for a, b in zip(inv, inv[1:])}) == 1
print('倒数', [float(v) for v in inv], '→ 下一项倒数', float(inv[-1] + F(1, 2)))
assert 1 / (inv[-1] + F(1, 2)) == nxt
print('答案：', [k for k, v in opts.items() if v == nxt], nxt)
