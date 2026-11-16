# 第32—34题：在小整数系数范围内搜索其他简单递推，看是否有别的规律能拟合已知各项并指向其他选项
from fractions import Fraction as F
from itertools import product
probs = {
    32: ([26, 61, 102, 151, 209, 277], {"A": 357, "B": 359, "C": 361, "D": 363}),
    33: ([28, 16, 30, 38, 53], {"A": 57, "B": 61, "C": 65, "D": 72}),
    34: ([51, 13, 2, 0, 1, 3], {"A": F(16, 3), "B": 5, "C": F(17, 2), "D": 8}),
}
half = [F(k, 2) for k in range(-6, 7)]
for no, (seq, opts) in probs.items():
    seq = [F(x) for x in seq]
    preds = {}
    n = len(seq)
    # 一阶：a(k+1) = p*a(k) + q*k + r
    for p, q in product(half, range(-10, 11)):
        r = [seq[k + 1] - p * seq[k] - q * k for k in range(n - 1)]
        if len(set(r)) == 1:
            preds.setdefault(p * seq[-1] + q * (n - 1) + r[0], []).append(f"a'={p}a{q:+d}k{r[0]:+}")
    # 二阶：a(k+2) = p*a(k+1) + s*a(k) + r
    for p, s in product(half, half):
        r = [seq[k + 2] - p * seq[k + 1] - s * seq[k] for k in range(n - 2)]
        if len(set(r)) == 1:
            preds.setdefault(p * seq[-1] + s * seq[-2] + r[0], []).append(f"a''={p}a'+{s}a{r[0]:+}")
    # 二阶乘积：a(k+2) = a(k)*a(k+1)*p + r
    for p in half:
        r = [seq[k + 2] - p * seq[k] * seq[k + 1] for k in range(n - 2)]
        if len(set(r)) == 1:
            preds.setdefault(p * seq[-1] * seq[-2] + r[0], []).append("prod")
    print(f"第{no}题 能拟合全部已知项的简单递推给出的下一项：",
          {str(k): v[:3] for k, v in preds.items()})
    print("   落在选项上的：", {o: str(v) for o, v in opts.items() if F(v) in preds})
