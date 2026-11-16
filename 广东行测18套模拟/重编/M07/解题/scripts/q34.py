# 第34题：51，13，2，0，1，3，（ ）  选项 A 16/3  B 5  C 17/2  D 8
from fractions import Fraction as F
seq = [F(x) for x in (51, 13, 2, 0, 1, 3)]
d1 = [b - a for a, b in zip(seq, seq[1:])]
d2 = [b - a for a, b in zip(d1, d1[1:])]
print("一级差", [str(x) for x in d1])   # -38 -11 -2 1 2
print("二级差", [str(x) for x in d2])   # 27 9 3 1
r = [b / a for a, b in zip(d2, d2[1:])]
print("二级差公比", [str(x) for x in r])
assert len(set(r)) == 1
nxt = seq[-1] + d1[-1] + d2[-1] * r[0]
print("答案", nxt)
opts = {"A": F(16, 3), "B": F(5), "C": F(17, 2), "D": F(8)}
print([k for k, v in opts.items() if v == nxt])
# 错误思路：一级差 -38,-11,-2,1,2 只看末两项“+1”，下一差取 3 → 6（不在选项）；把二级差末项看成 1 不变 → 3+3=6；
# 二级差取 0 → 5（B）
print("若下一二级差取0 →", seq[-1] + d1[-1])
