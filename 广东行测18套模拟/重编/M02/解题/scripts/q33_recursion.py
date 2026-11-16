"""第33题：37，25，87，199，485，（ ）  选项 A1901 B1836 C1685 D1169

核验思路：数列先降后急升，作差无规律；搜索 a(n)=p*a(n-1)+q*a(n-2)+r 型递推（p、q、r 为小整数），
看能否唯一拟合已知 5 项，再用拟合出的递推算下一项，并核对选项。
"""
from itertools import product

seq = [37, 25, 87, 199, 485]
options = {"A": 1901, "B": 1836, "C": 1685, "D": 1169}

print("一级差", [seq[i + 1] - seq[i] for i in range(4)])

fits = []
for p, q, r in product(range(-5, 6), range(-5, 6), range(-100, 101)):
    if all(seq[i] == p * seq[i - 1] + q * seq[i - 2] + r for i in range(2, 5)):
        fits.append((p, q, r))
print("拟合的递推 (p,q,r):", fits)
for p, q, r in fits:
    nxt = p * seq[-1] + q * seq[-2] + r
    hit = [k for k, v in options.items() if v == nxt]
    print("  a(n)=%d*a(n-1)+%d*a(n-2)+%d -> 下一项 %d，对应选项 %s" % (p, q, r, nxt, hit))

# 逐项展示：前一项×2+再前一项
for i in range(2, 5):
    print("%d×2+%d=%d" % (seq[i - 1], seq[i - 2], 2 * seq[i - 1] + seq[i - 2]))
print("485×2+199 =", 485 * 2 + 199)
