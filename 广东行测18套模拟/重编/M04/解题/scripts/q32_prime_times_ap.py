"""第32题：6，21，55，105，209，（ ）
因数分解：6=2×3，21=3×7，55=5×11，105=7×15，209=11×19。
第一个因数为质数列 2,3,5,7,11,(13)；第二个因数为公差4的等差数列 3,7,11,15,19,(23)。
同时检查常见的其他规律（多级差、二阶线性递推）能否给出某个选项。
"""
from fractions import Fraction
from itertools import product

seq = [6, 21, 55, 105, 209]
options = {"A": 197, "B": 268, "C": 299, "D": 400}

primes = [2, 3, 5, 7, 11, 13]
ap = [3 + 4 * i for i in range(6)]
pred = [p * q for p, q in zip(primes, ap)]
print("质数×等差：", list(zip(primes, ap)), "->", pred)
assert pred[:5] == seq
print("预测第6项 =", pred[5], "吻合选项:", [k for k, v in options.items() if v == pred[5]])

# 多级差
d1 = [b - a for a, b in zip(seq, seq[1:])]
d2 = [b - a for a, b in zip(d1, d1[1:])]
d3 = [b - a for a, b in zip(d2, d2[1:])]
print("一级差", d1, "二级差", d2, "三级差", d3, "（无明显规律）")

# 一阶线性递推 a(n+1)=p*a(n)+q：用前两组解出 p,q，看是否与后面一致
def solve2(a1, b1, c1, a2, b2, c2):
    det = a1 * b2 - a2 * b1
    if det == 0:
        return None
    return Fraction(c1 * b2 - c2 * b1, det), Fraction(a1 * c2 - a2 * c1, det)

pq = solve2(seq[0], 1, seq[1], seq[1], 1, seq[2])
print("一阶线性递推拟合 p,q =", pq, "检验后项:", [pq[0] * seq[i] + pq[1] for i in range(2, 4)], "实际", seq[3:5])

# 每项=前一项×k+常数(小整数)扫描：是否有某个整数 k 使 a(n+1)-k*a(n) 成简单规律
for k in range(1, 4):
    r = [b - k * a for a, b in zip(seq, seq[1:])]
    print(f"a(n+1)-{k}a(n):", r)

ans = [k for k, v in options.items() if v == pred[5]]
assert ans == ["C"]
print("答案:", ans[0])
