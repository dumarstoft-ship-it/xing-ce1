"""M05 第31题：14，39，65，94，132，197，（ ）

思路：多级作差。一级差 25,26,29,38,65；二级差 1,3,9,27 是公比为3的等比数列。
把四个选项分别接到数列末尾，检验哪个能让二级差保持公比3；
再用小整数系数的线性递推 a(n+2)=p*a(n+1)+q*a(n)+r 做一遍无偏搜索，看能拟合已知项的规律预测什么。
"""
from fractions import Fraction

seq = [14, 39, 65, 94, 132, 197]
options = {"A": 343, "B": 313, "C": 278, "D": 211}


def diffs(s):
    return [b - a for a, b in zip(s, s[1:])]


d1 = diffs(seq)
d2 = diffs(d1)
print("一级差:", d1)
print("二级差:", d2)
print("二级差相邻比:", [str(Fraction(b, a)) for a, b in zip(d2, d2[1:])])
assert all(Fraction(b, a) == 3 for a, b in zip(d2, d2[1:]))
print("三级差（无规律，不继续作差）:", diffs(d2))

hits = []
for k, v in options.items():
    e2 = diffs(diffs(seq + [v]))
    ok = all(Fraction(b, a) == 3 for a, b in zip(e2, e2[1:]))
    print(f"{k} {v}: 二级差 {e2} -> {'符合' if ok else '不符'}")
    if ok:
        hits.append(k)
assert hits == ["A"], hits

# 无偏搜索：a(n+2) = p*a(n+1) + q*a(n) + r，p,q 取 -5..5
fits = []
for p in range(-5, 6):
    for q in range(-5, 6):
        r = seq[2] - p * seq[1] - q * seq[0]
        if all(seq[i + 2] == p * seq[i + 1] + q * seq[i] + r for i in range(len(seq) - 2)):
            fits.append((p, q, r, p * seq[-1] + q * seq[-2] + r))
print("能拟合全部已知项的二阶线性递推 (p,q,r,预测):", fits)
assert fits and all(f[3] == 343 for f in fits)

print("答案: A 343（下一个二级差81，一级差65+81=146，197+146=343）")
