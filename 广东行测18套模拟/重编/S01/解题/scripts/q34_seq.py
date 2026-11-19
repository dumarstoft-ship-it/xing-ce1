"""S01 第34题：1/3，1，9/5，8/3，（ ）  选项 A29/11 B29/9 C25/8 D25/7（原卷公式图，已核对）
改写为 1/3、4/4、9/5、16/6：分子1、4、9、16是平方数，分母3、4、5、6连续 → 25/7。"""
from fractions import Fraction as F
seq = [F(1, 3), F(1), F(9, 5), F(8, 3)]
assert seq == [F(n * n, n + 2) for n in range(1, 5)]
nxt = F(25, 7)
opts = {'A': F(29, 11), 'B': F(29, 9), 'C': F(25, 8), 'D': F(25, 7)}
print('答案：', [k for k, v in opts.items() if v == nxt])
# 检查：数列递增，各项差 2/3、4/5、13/15，下一项应大于8/3≈2.667；A=2.636<8/3
print({k: round(float(v), 4) for k, v in opts.items()}, '8/3=', round(8 / 3, 4))
