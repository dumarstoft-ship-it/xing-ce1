# -*- coding: utf-8 -*-
"""M09 第53题（GD2023-XJ-Q056）、第61题（GD2019-XJ-Q049）：枚举全部情形核验“必然正确”。"""
from itertools import product, permutations

# ---------- 第53题 ----------
men, women = ["甲", "乙", "丙"], ["张", "李", "王"]
people = men + women
sols = []
for assign in product("ABCD", repeat=6):
    a = dict(zip(people, assign))
    # ②有男性去的社区必须有女性
    if any(a[m] not in {a[w] for w in women} for m in men):
        continue
    # ③张去A或B，乙去D；附加条件：李去C
    if a["张"] not in "AB" or a["乙"] != "D" or a["李"] != "C":
        continue
    sols.append(a)
opts53 = {"A 丙去A": lambda a: a["丙"] == "A", "B 张去B": lambda a: a["张"] == "B",
          "C 甲去C": lambda a: a["甲"] == "C", "D 王去D": lambda a: a["王"] == "D"}
print(f"第53题：满足条件的去法共{len(sols)}种")
for k, f in opts53.items():
    n = sum(f(a) for a in sols)
    print(f"  {k}：{n}/{len(sols)}种成立{'（必然）' if n == len(sols) else ''}")

# ---------- 第61题 ----------
degrees = ["教育学硕士", "教育学学士", "哲学硕士", "哲学学士"]
ok = []
for p in permutations(degrees):
    d = dict(zip("甲乙丙丁", p))
    subj = {k: v[:-2] for k, v in d.items()}
    if d["甲"] in ("教育学硕士", "哲学学士"):
        continue
    if subj["甲"] != subj["丙"]:
        continue
    if not d["乙"].endswith("学士"):
        continue
    if subj["丁"] == "哲学":
        continue
    ok.append(d)
print(f"\n第61题：满足条件的分配共{len(ok)}种：{ok}")
opts61 = {"A 甲是教育学学士": ("甲", "教育学学士"), "B 乙是哲学学士": ("乙", "哲学学士"),
          "C 丙是哲学学士": ("丙", "哲学学士"), "D 丁是教育学学士": ("丁", "教育学学士")}
for k, (who, deg) in opts61.items():
    print(f"  {k}：{'正确' if all(d[who] == deg for d in ok) else '错误'}")
