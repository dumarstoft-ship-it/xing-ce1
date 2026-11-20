"""S02 第34题：1/5，1/5，3/17，2/13，（ ）  选项 A2/13 B1/11 C4/35 D5/37（原卷公式图，已核对）
反约分：1/5、2/10、3/17、4/26，分子1、2、3、4，分母n²+1（5、10、17、26）→ 5/37。"""
from fractions import Fraction as F
seq = [F(1, 5), F(1, 5), F(3, 17), F(2, 13)]
assert seq == [F(n, (n + 1) ** 2 + 1) for n in range(1, 5)]
nxt = F(5, 6 ** 2 + 1)
opts = {'A': F(2, 13), 'B': F(1, 11), 'C': F(4, 35), 'D': F(5, 37)}
print('下一项', nxt, '答案：', [k for k, v in opts.items() if v == nxt])
assert nxt == F(5, 37)
