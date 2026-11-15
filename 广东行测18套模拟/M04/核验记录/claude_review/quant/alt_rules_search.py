#!/usr/bin/env python3
"""数字推理第31-35题：对每个选项做"简单规律族"搜索，看错误选项是否也能被一条同样自然的规律解释。
规律族（启发式，非穷尽）：
  F1 原数列 / 一次差 / 二次差 为等差（k阶常差，k<=3，需至少留2项检验）
  F2 一次差或二次差 为等比（公比为整数或半整数）
  F3 二阶线性递推 a_n = p*a_{n-1} + q*a_{n-2} + r，p,q ∈ {-2,-3/2,...,3}，r 为整数/半整数 |r|<=40，所有方程均需成立
  F4 a_n = p*a_{n-1} + c_n，c_n 为等差或等比（p ∈ {1/2,1,3/2,2,3}）
  F5 平方根/立方根数列满足 F1/F3
可独立重跑：python3 alt_rules_search.py
"""
from fractions import Fraction as F
from itertools import product

def diffs(xs):
    return [b - a for a, b in zip(xs, xs[1:])]

def is_const(xs):
    return len(xs) >= 2 and all(x == xs[0] for x in xs)

def is_arith(xs):
    return len(xs) >= 3 and is_const(diffs(xs))

def is_geom(xs):
    if len(xs) < 3 or any(x == 0 for x in xs):
        return False
    r = [F(b) / F(a) for a, b in zip(xs, xs[1:])]
    return is_const(r)

HALF = [F(k, 2) for k in range(-6, 7)]

def rules(seq):
    found = []
    s = [F(x) for x in seq]
    # F1
    cur = s
    for k in range(0, 3):
        if len(cur) >= 3 and is_const(diffs(cur)) and len(diffs(cur)) >= 2:
            found.append(f"F1:{k}次差等差(常差{diffs(cur)[0]})")
        cur = diffs(cur)
    # F2
    d1 = diffs(s); d2 = diffs(d1)
    if is_geom(d1) and len(d1) >= 3:
        found.append("F2:一次差等比")
    if is_geom(d2) and len(d2) >= 3:
        found.append("F2:二次差等比")
    # F3
    if len(s) >= 5:
        for p, q in product(HALF, HALF):
            if p == 0 and q == 0:
                continue
            r = s[2] - p * s[1] - q * s[0]
            if r.denominator > 2 or abs(r) > 40:
                continue
            if all(s[i] == p * s[i - 1] + q * s[i - 2] + r for i in range(3, len(s))):
                found.append(f"F3:a=({p})a1+({q})a2+({r})")
    # F4
    for p in (F(1, 2), F(1), F(3, 2), F(2), F(3)):
        c = [s[i] - p * s[i - 1] for i in range(1, len(s))]
        if len(c) >= 4 and (is_arith(c) or is_geom(c)):
            found.append(f"F4:a=({p})a1+c, c={[str(x) for x in c]}")
    return found

def roots(seq, k):
    out = []
    for x in seq:
        r = round(abs(x) ** (1 / k))
        if r ** k != x:
            return None
        out.append(r)
    return out

cases = {
    31: ([14, 39, 65, 94, 132, 197], dict(A=343, B=313, C=278, D=211)),
    33.1: ([2, 5, 11, 20], dict(A=32, B=32, C=47, D=47)),
    33.2: ([4, 12, 36, 108], dict(A=324, B=216, C=324, D=216)),
    34: ([F(26), F(12), F(25), F(31), F(87, 2)], dict(A=F(53), B=F(113, 2), C=F(59), D=F(125, 2))),
    35: ([16, 4, 36, 64, 196], dict(A=441, B=484, C=576, D=625)),
    32: ([F(40), F(43), F(48), F(55), F(64)], dict(A=F(87), B=F(75), C=F(66), D=F(88))),  # 通分到96后的分子
}
for qid, (seq, opts) in cases.items():
    print(f"== Q{qid} 已知 {[str(x) for x in seq]}")
    for k, v in opts.items():
        r = rules(list(seq) + [v])
        extra = []
        if qid == 35:
            rt = roots(list(seq) + [v], 2)
            if rt:
                extra = ["F5(平方根):" + x for x in rules(rt)]
        print(f"  {k}={v}: {r + extra if (r or extra) else '无简单规律'}")
