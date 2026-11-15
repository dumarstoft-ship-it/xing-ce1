# -*- coding: utf-8 -*-
"""Blind solve for Q57: exhaustive search over 6^4 = 1296 order combinations."""
from itertools import combinations, product

DISHES = ["芹菜肉丝", "清蒸鲈鱼", "毛豆仔鸡", "糖醋排骨"]
Q, L, M, T = DISHES
PEOPLE = ["甲", "乙", "丙", "丁"]
PAIRS = [frozenset(c) for c in combinations(DISHES, 2)]
assert len(PAIRS) == 6

def imp(p, q):
    return (not p) or q

def base_ok(o):
    for d in DISHES:
        n = sum(d in o[p] for p in PEOPLE)
        if n == 4 or n == 0:       # no dish ordered by all four / by none
            return False
    return True

def c1_necessary(o):   # 只有甲点清蒸鲈鱼，丁才点芹菜肉丝 : 丁Q -> 甲L
    return imp(Q in o["丁"], L in o["甲"])

def c1_sufficient_misread(o):   # misreading: 甲L -> 丁Q
    return imp(L in o["甲"], Q in o["丁"])

def c2(o):   # 丙L -> 乙L and 丁L
    return imp(L in o["丙"], L in o["乙"] and L in o["丁"])

def c3(o):   # (乙Q or 乙L) -> 乙M
    return imp(Q in o["乙"] or L in o["乙"], M in o["乙"])

def c4(o):   # (丙Q or 丙M) -> 丙L
    return imp(Q in o["丙"] or M in o["丙"], L in o["丙"])

OPTIONS = {
    "A": lambda o: Q in o["甲"] or M in o["甲"],
    "B": lambda o: Q in o["乙"] or T in o["乙"],
    "C": lambda o: M in o["丙"] or T in o["丙"],
    "D": lambda o: Q in o["丁"] or M in o["丁"],
}

def fmt(o):
    return "  ".join(p + "{" + "、".join(d for d in DISHES if d in o[p]) + "}" for p in PEOPLE)

def solve(conds, label, show=False):
    total = 0
    sols = []
    for combo in product(PAIRS, repeat=4):
        total += 1
        o = dict(zip(PEOPLE, combo))
        if base_ok(o) and all(c(o) for c in conds):
            sols.append(o)
    print(f"\n=== {label}: searched {total} combos, valid = {len(sols)}")
    for k, f in OPTIONS.items():
        t = sum(f(o) for o in sols)
        status = "必然成立" if t == len(sols) else ("必然不成立" if t == 0 else "可真可假")
        print(f"  option {k}: true in {t}/{len(sols)} -> {status}")
    if show:
        for o in sols:
            print("   ", fmt(o))
    # per-person possible orders
    for p in PEOPLE:
        poss = sorted({"、".join(d for d in DISHES if d in o[p]) for o in sols})
        print(f"  {p} possible: {poss}")
    return sols

sols = solve([c1_necessary, c2, c3, c4], "Stated conditions (1 read as necessary condition)", show=True)
solve([c1_sufficient_misread, c2, c3, c4], "Variant: (1) misread as 甲L -> 丁Q")
solve([c2, c3, c4], "Variant: (1) dropped")
solve([c1_necessary, c2, c4], "Variant: (3) dropped")
solve([c1_necessary, c3, c4], "Variant: (2) dropped")
solve([c1_necessary, c2, c3], "Variant: (4) dropped")

# check what happens without the 'no dish ordered by all four' clause
def base_no_all4_only_none(o):
    return all(sum(d in o[p] for p in PEOPLE) > 0 for d in DISHES)
cnt = 0; truthA = 0
for combo in product(PAIRS, repeat=4):
    o = dict(zip(PEOPLE, combo))
    if base_no_all4_only_none(o) and all(c(o) for c in (c1_necessary, c2, c3, c4)):
        cnt += 1; truthA += OPTIONS["A"](o)
print(f"\n=== Variant: drop 'no dish ordered by all four': valid={cnt}, option A true in {truthA}")

# check: drop 'no dish ordered by none' (keep 'not all four')
cnt = 0; tally = {k: 0 for k in OPTIONS}
for combo in product(PAIRS, repeat=4):
    o = dict(zip(PEOPLE, combo))
    if all(sum(d in o[p] for p in PEOPLE) < 4 for d in DISHES) and all(c(o) for c in (c1_necessary, c2, c3, c4)):
        cnt += 1
        for k, f in OPTIONS.items():
            tally[k] += f(o)
print(f"=== Variant: drop 'no dish ordered by none': valid={cnt}, option truth counts={tally}")
