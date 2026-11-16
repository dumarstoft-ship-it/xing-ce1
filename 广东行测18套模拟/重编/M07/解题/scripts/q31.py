# 第31题：4/3，1/2，1/2，7/10，7/9，（ ）
# 选项（转写）：A 2/3  B 13/18  C 2/7  D 14/17
from fractions import Fraction as F
from itertools import product
import json, os

seq = [F(4, 3), F(1, 2), F(1, 2), F(7, 10), F(7, 9)]
opts = {"A": F(2, 3), "B": F(13, 18), "C": F(2, 7), "D": F(14, 17)}

# 1) 反约分：4/3，2/4，3/6，7/10，14/18
P = [4, 2, 3, 7, 14]
Q = [3, 4, 6, 10, 18]
assert all(F(p, q) == s for p, q, s in zip(P, Q, seq))
dP = [b - a for a, b in zip(P, P[1:])]      # -2,1,4,7 公差3
dQ = [b - a for a, b in zip(Q, Q[1:])]      # 1,2,4,8 公比2
print("分子", P, "一级差", dP)
print("分母", Q, "一级差", dQ)
nP = P[-1] + dP[-1] + 3                      # 14+10=24
nQ = Q[-1] + dQ[-1] * 2                      # 18+16=34
ans = F(nP, nQ)
print("下一项", f"{nP}/{nQ}", "=", ans)       # 24/34 = 12/17
print("与转写选项相符的：", [k for k, v in opts.items() if v == ans] or "无")

# 2) 若选项C原为12/17，则其余三项恰好是“漏接一个球”的结果：
print("A 2/3 =24/36：分子对，分母误按“直接翻倍”18×2=36 →", F(24, 36))
print("D 14/17=28/34：分母对，分子误看成7→14→28翻倍 →", F(28, 34))
print("B 13/18=26/36：分子按14×2-2=26、分母按18×2=36 →", F(26, 36))

# 3) 小范围穷举：每项反约分倍数1..12，分子、分母各试常见规律（等差、二级等差、差等比、
#    x→ax+b、两项递推及分子分母交叉的一阶/二阶线性关系），看能否得到四个转写选项之一
def single(xs):
    out = []
    d = [xs[i + 1] - xs[i] for i in range(4)]
    if len(set(d)) == 1: out.append(xs[4] + d[0])
    dd = [d[i + 1] - d[i] for i in range(3)]
    if len(set(dd)) == 1: out.append(xs[4] + d[3] + dd[0])
    if 0 not in d:
        r = [F(d[i + 1], d[i]) for i in range(3)]
        if len(set(r)) == 1: out.append(xs[4] + d[3] * r[0])
    if 0 not in xs:
        r = [F(xs[i + 1], xs[i]) for i in range(4)]
        if len(set(r)) == 1: out.append(xs[4] * r[0])
    for a in (-2, -1, 2, 3):
        b = [xs[i + 1] - a * xs[i] for i in range(4)]
        if len(set(b)) == 1: out.append(a * xs[4] + b[0])
    c = [xs[i + 2] - xs[i] - xs[i + 1] for i in range(3)]
    if len(set(c)) == 1: out.append(xs[3] + xs[4] + c[0])
    return out

coef = (-2, -1, 0, 1, 2)
found = {}
for ks in product(range(1, 13), repeat=5):
    PP = [s.numerator * k for s, k in zip(seq, ks)]
    QQ = [s.denominator * k for s, k in zip(seq, ks)]
    S = {"P": PP, "Q": QQ}
    pred = {}
    for X in "PQ":
        xs = S[X]
        L = single(xs)
        for a, b in product(coef, coef):
            if a == 0 and b == 0: continue
            g = [xs[i + 1] - a * PP[i] - b * QQ[i] for i in range(4)]
            if len(set(g)) == 1: L.append(a * PP[4] + b * QQ[4] + g[0])
        for A, B in product("PQ", "PQ"):
            for a, b in product(coef, coef):
                if a == 0 or b == 0: continue
                g = [xs[i + 2] - a * S[A][i] - b * S[B][i + 1] for i in range(3)]
                if len(set(g)) == 1 and abs(g[0]) <= 10: L.append(a * S[A][3] + b * S[B][4] + g[0])
        pred[X] = set(L)
    for p, q in product(pred["P"], pred["Q"]):
        if q != 0:
            v = F(p) / F(q)
            found.setdefault(v, ks)
print("穷举得到的下一项取值：", {str(k): v for k, v in found.items()})
print("其中属于转写选项的：", [k for k, v in opts.items() if v in found] or "无")

# 4) 选项C图片的哈希核对：同一分式的公式图在各季通常逐字节相同（如2/3在8季中哈希一致），
#    而两张转写为2/7的图哈希不同
rec = "/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/转写核验记录.json"
if os.path.exists(rec):
    d = json.load(open(rec, encoding="utf-8"))
    def walk(x):
        if isinstance(x, dict):
            yield x
            for v in x.values(): yield from walk(v)
        elif isinstance(x, list):
            for v in x: yield from walk(v)
    for t in ("$\\frac{2}{3}$", "$\\frac{2}{7}$"):
        rows = [(it["asset_id"], it["source_image_sha256"][:12]) for it in walk(d)
                if it.get("type") == "formula_text" and it.get("text") == t]
        print(t, rows)
