# -*- coding: utf-8 -*-
"""M09 第51题（GD2023-XJ-Q069）、第57题（GD2022-XJ-Q057）：条件推理的真值表核验。

第51题：把题干和各选项都写成“条件句＋小前提⇒结论”，看推理形式（肯前/否前/肯后/否后）与是否有效。
第57题：名不正→言不顺→事不成→礼乐不兴→刑罚不中→民无所措手足，穷举6个命题的真假，
检查①～④在所有满足题干的情形下是否都成立。
"""
from itertools import product


def valid(premises, conclusion, n):
    return all(conclusion(*v) for v in product([True, False], repeat=n) if all(p(*v) for p in premises))


def imp(a, b):
    return (not a) or b


# ---------- 第51题 ----------
# 每项：条件句（统一译成 前件→后件）、小前提、结论；变量 x,y
Q51 = {
    "题干": ("获奖→练习（只有练习才获奖）", lambda x, y: imp(x, y), lambda x, y: not x, lambda x, y: not y, "否前"),
    "A": ("利润上涨→降低成本（必要条件）", lambda x, y: imp(x, y), lambda x, y: not x, lambda x, y: not y, "否前"),
    "B": ("优秀销售员→能力过硬（除非…否则不…）", lambda x, y: imp(x, y), lambda x, y: x, lambda x, y: y, "肯前"),
    "C": ("最大程度减排→践行低碳出行（如果…那么就要…）", lambda x, y: imp(x, y), lambda x, y: not y, lambda x, y: not x, "否后"),
    "D": ("价格大幅下降→销量迅速上升（如果…就…）", lambda x, y: imp(x, y), lambda x, y: not y, lambda x, y: not x, "否后"),
}

# ---------- 第57题 ----------
# 变量：名正 言顺 事成 礼乐兴 刑罚中 民无所措
def stem57(m, y, s, l, x, w):
    return imp(not m, not y) and imp(not y, not s) and imp(not s, not l) and imp(not l, not x) and imp(not x, w)


Q57 = {
    "①名正则言顺": lambda m, y, s, l, x, w: imp(m, y),
    "②礼乐兴则事已成": lambda m, y, s, l, x, w: imp(l, s),
    "③名不正，则民无所措手足": lambda m, y, s, l, x, w: imp(not m, w),
    "④只有名正言顺才事可成": lambda m, y, s, l, x, w: imp(s, m and y),
}

if __name__ == "__main__":
    print("第51题")
    for k, (desc, cond, minor, concl, form) in Q51.items():
        ok = valid([cond, minor], concl, 2)
        print(f"  {k}：{desc}；形式＝{form}；推理{'有效' if ok else '无效'}")
    print("  题干与A同为“否前推否后”（无效）；B肯前、C/D否后（有效），形式不同。\n")
    print("第57题")
    for k, f in Q57.items():
        print(f"  {k}：{'必然为真' if valid([stem57], f, 6) else '不必然（有反例）'}")
    print("  ⇒ ②③④必然为真，选C。")
