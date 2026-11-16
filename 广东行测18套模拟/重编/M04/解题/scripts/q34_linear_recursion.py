"""第34题：5，-14，43，-128，385，（ ）
拟合一阶线性递推 a(n+1)=p*a(n)+q：用前两组相邻关系解 p、q，再用后两组检验。
"""
from fractions import Fraction as F

seq = [5, -14, 43, -128, 385]
a1, b1 = seq[0], seq[1]
a2, b2 = seq[1], seq[2]
p = F(b1 - b2, a1 - a2)
q = b1 - p * a1
print("p =", p, "q =", q)
for i in range(len(seq) - 1):
    print(f"{seq[i]} * {p} + {q} = {p * seq[i] + q}  实际 {seq[i+1]}")
    assert p * seq[i] + q == seq[i + 1]
nxt = p * seq[-1] + q
print("下一项 =", nxt)
options = {"A": 1513, "B": -1513, "C": 1154, "D": -1154}
hits = [k for k, v in options.items() if v == nxt]
print("吻合选项:", hits)
assert hits == ["D"]
