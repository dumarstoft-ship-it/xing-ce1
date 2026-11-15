#!/usr/bin/env python3
"""M04 第56题 穷举验证（只依据题本可见内容）。

形式化：
  人员 P = {甲, 乙, 丙, 丁}；每人三个布尔属性 male / party / prof。
  组长 = 同时为 男性 ∧ 党员 ∧ 教授 的那位专家（题干：组长在4人之中）。
  (1) ∀p: male(p) ∨ party(p) ∨ prof(p)
  (2) |party| = 3, |male| = 2, |prof| = 1
  (3) male(甲) ↔ male(乙)
  (4) party(乙) ↔ party(丙)
  (5) ¬(party(丙) ∧ party(丁))
  (L) ∃p: male(p) ∧ party(p) ∧ prof(p)        —— “担任组长的专家为男性、党员、教授”
另外给出去掉 (L) 时的解集，作为“组长是否必须在4人中”这一隐含前提的对照。

运行：python3 verify_q56.py
"""
from itertools import product

P = ["甲", "乙", "丙", "丁"]


def solve(require_leader=True):
    sols = []
    for bits in product([0, 1], repeat=12):
        male = dict(zip(P, bits[0:4]))
        party = dict(zip(P, bits[4:8]))
        prof = dict(zip(P, bits[8:12]))
        if not all(male[p] or party[p] or prof[p] for p in P):
            continue
        if sum(party.values()) != 3 or sum(male.values()) != 2 or sum(prof.values()) != 1:
            continue
        if male["甲"] != male["乙"]:
            continue
        if party["乙"] != party["丙"]:
            continue
        if party["丙"] and party["丁"]:
            continue
        leaders = [p for p in P if male[p] and party[p] and prof[p]]
        if require_leader and not leaders:
            continue
        sols.append((male, party, prof, leaders))
    return sols


if __name__ == "__main__":
    for req in (True, False):
        sols = solve(req)
        print(f"require_leader={req}: {len(sols)} 个解")
        for male, party, prof, leaders in sols:
            row = []
            for p in P:
                tags = []
                if male[p]:
                    tags.append("男")
                if party[p]:
                    tags.append("党")
                if prof[p]:
                    tags.append("教")
                row.append(f"{p}:{''.join(tags) or '-'}")
            print("   ", "  ".join(row), "| 组长:", leaders or "无")
    leaders = {tuple(s[3]) for s in solve(True)}
    print("组长集合（全部解）:", leaders)
    assert leaders == {("丙",)}, leaders
    print("结论：组长唯一为 丙 → 选项 C")
