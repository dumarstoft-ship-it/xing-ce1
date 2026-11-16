# 第31—35题：排查“别的简单规律”是否也能拟合已知项并落到某个选项上。
# 搜索范围：a(n)=p·a(n-2)+q·a(n-1)+r（p,q∈[-4,4]，r∈[-20,20]）；
#           a(n)=p·a(n-2)·a(n-1)+r；a(n)=p·a(n-1)+r·n+c；三阶线性 a(n)=p·a(n-3)+q·a(n-2)+t·a(n-1)。
from fractions import Fraction as F
import itertools

seqs = {
    31: ([2, 5, 3, 7, 2, 11, 12], [2, 3, 4, 5]),
    32: ([8, 15, 26, 39, 56], [72, 75, 84, 89]),
    33: ([9, 63, 217, 511], [999, 1001, 1023, 1025]),
    34: ([1, 15, 12, 4, 1], [0, 1, 2, 3]),
    35: ([F(9), F(45), F(54), F(57), F(117, 2)], [F(117, 2), F(59), F(119, 2), F(60)]),
}
rng = range(-4, 5)
for q, (s, opts) in seqs.items():
    found = {}
    for p, qq, r in itertools.product(rng, rng, range(-20, 21)):
        if all(s[i] == p * s[i - 2] + qq * s[i - 1] + r for i in range(2, len(s))):
            found.setdefault(p * s[-2] + qq * s[-1] + r, []).append(("lin2", p, qq, r))
    for p, r in itertools.product([1, -1, F(1, 2), 2], range(-30, 31)):
        if all(s[i] == p * s[i - 2] * s[i - 1] + r for i in range(2, len(s))):
            found.setdefault(p * s[-2] * s[-1] + r, []).append(("prod", p, r))
    for p, r, c in itertools.product(rng, range(-10, 11), range(-30, 31)):
        if all(s[i] == p * s[i - 1] + r * i + c for i in range(1, len(s))):
            found.setdefault(p * s[-1] + r * len(s) + c, []).append(("lin1n", p, r, c))
    if len(s) >= 6:
        for p, qq, t in itertools.product(rng, rng, rng):
            if all(s[i] == p * s[i - 3] + qq * s[i - 2] + t * s[i - 1] for i in range(3, len(s))):
                found.setdefault(p * s[-3] + qq * s[-2] + t * s[-1], []).append(("lin3", p, qq, t))
    hits = {str(k): v[:3] for k, v in found.items() if k in opts}
    print("第%d题：能拟合已知项的简单递推 %d 个；落到选项上的：%s" % (q, len(found), hits or "无"))
    assert not hits
