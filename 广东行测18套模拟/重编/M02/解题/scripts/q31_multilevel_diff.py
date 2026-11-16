"""第31题：3，16，43，88，155，（ ）  选项 A186 B209 C248 D261

核验思路：
1. 逐级作差，看第几级出现等差/常数。
2. 把四个选项分别接到数列末尾，检查哪一个能让"二级差成等差（三级差为常数）"成立。
3. 顺带试几种常见的其他规律（n^3+修正、相邻项递推），确认没有别的选项也能讲通。
"""
from itertools import product

seq = [3, 16, 43, 88, 155]
options = {"A": 186, "B": 209, "C": 248, "D": 261}


def diffs(a):
    return [a[i + 1] - a[i] for i in range(len(a) - 1)]


d1 = diffs(seq)
d2 = diffs(d1)
d3 = diffs(d2)
print("一级差", d1)   # [13, 27, 45, 67]
print("二级差", d2)   # [14, 18, 22]
print("三级差", d3)   # [4, 4]

nxt_d2 = d2[-1] + d3[-1]          # 26
nxt_d1 = d1[-1] + nxt_d2          # 93
pred = seq[-1] + nxt_d1           # 248
print("推得下一项", pred)

for k, v in options.items():
    s = seq + [v]
    ok = len(set(diffs(diffs(diffs(s))))) == 1
    print(k, v, "三级差为常数" if ok else "不满足", diffs(diffs(diffs(s))))

# 其他常见规律：n^3 + 修正项 ；a(n)=p*a(n-1)+q*a(n-2)+r（小整数）
print("n^3 修正项:", [seq[i] - (i + 1) ** 3 for i in range(5)])
print("n^2 修正项:", [seq[i] - (i + 1) ** 2 for i in range(5)])
hits = []
for p, q, r in product(range(-4, 5), range(-4, 5), range(-60, 61)):
    if all(seq[i] == p * seq[i - 1] + q * seq[i - 2] + r for i in range(2, 5)):
        hits.append((p, q, r))
print("二阶线性递推（小整数系数）拟合结果:", hits)
