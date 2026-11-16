"""第43题：螺丝钉、螺丝帽一一配套。A车间每小时40钉或50帽，B车间每小时30钉或60帽；
单独生产这批螺丝钉，A比B少用20小时。两车间合作最少需要多少小时（不足1小时按1小时计）？
选项 A51 B52 C53 D54

核验：
1. 由 N/30 - N/40 = 20 求出螺丝钉（=螺丝帽）数量 N；
2. 线性规划（顶点枚举，精确分数）求连续时间下的最短完工时间；
3. 按整小时分配枚举，求整数小时下的最短完工时间，两者互相印证。
"""
from fractions import Fraction as F
from itertools import combinations
from math import ceil

# 1. 求 N
N = [n for n in range(1, 100001) if F(n, 30) - F(n, 40) == 20]
print("满足 N/30-N/40=20 的 N:", N)
N = N[0]

# 2. LP：变量 x = (ab, an, bb, bn, T)，A造钉/帽时间、B造钉/帽时间、完工时间；约束写成 g·x >= h
cons = [
    ([40, 0, 30, 0, 0], N),     # 钉够
    ([0, 50, 0, 60, 0], N),     # 帽够
    ([-1, -1, 0, 0, 1], 0),     # A 的总用时 <= T
    ([0, 0, -1, -1, 1], 0),     # B 的总用时 <= T
    ([1, 0, 0, 0, 0], 0),
    ([0, 1, 0, 0, 0], 0),
    ([0, 0, 1, 0, 0], 0),
    ([0, 0, 0, 1, 0], 0),
    ([0, 0, 0, 0, 1], 0),
]


def solve(rows, rhs):
    n = len(rows)
    m = [[F(v) for v in r] + [F(b)] for r, b in zip(rows, rhs)]
    for col in range(n):
        piv = next((r for r in range(col, n) if m[r][col] != 0), None)
        if piv is None:
            return None
        m[col], m[piv] = m[piv], m[col]
        for r in range(n):
            if r != col and m[r][col] != 0:
                f = m[r][col] / m[col][col]
                m[r] = [a - f * b for a, b in zip(m[r], m[col])]
    return [m[i][n] / m[i][i] for i in range(n)]


best = None
for idx in combinations(range(len(cons)), 5):
    x = solve([cons[i][0] for i in idx], [cons[i][1] for i in idx])
    if x is None:
        continue
    if all(sum(g * v for g, v in zip(c[0], x)) >= c[1] for c in cons):
        if best is None or x[4] < best[4]:
            best = x
ab, an, bb, bn, T = best
print("LP 最优: A造钉 %s h, A造帽 %s h, B造钉 %s h, B造帽 %s h, 完工 T=%s h ≈ %.4f h"
      % (ab, an, bb, bn, T, float(T)))
print("按'不足1小时按1小时计' => %d 小时" % ceil(T))

# 3. 整小时分配枚举：每个车间在 T 小时内把整数小时分给钉和帽
def feasible_int(T):
    for ab in range(T + 1):
        for bb in range(T + 1):
            if 40 * ab + 30 * bb >= N and 50 * (T - ab) + 60 * (T - bb) >= N:
                return (ab, T - ab, bb, T - bb)
    return None


for T in range(48, 56):
    print("T=%d 小时可行分配:" % T, feasible_int(T))

# 对照几种常见错误思路
print("两车间同时先做钉再做帽:", float(F(N, 70) + F(N, 110)))
print("A全做帽、B全做钉（分工反了）:", max(float(F(N, 50)), float(F(N, 30))))
