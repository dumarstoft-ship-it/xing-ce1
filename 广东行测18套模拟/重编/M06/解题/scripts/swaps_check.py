"""M06换入题复算：第37题（JS2021-A类-054，行程）、第60题（ZJ2025-A类-102，分析推理）。"""
import itertools
from fractions import Fraction

# 第37题：甲用120分钟，乙用100分钟；甲每分钟比乙多10米，甲多走2800米
sols = [x for x in range(1, 1000) if 120 * (x + 10) - 100 * x == 2800]
assert sols == [80]
print("第37题：乙", sols[0], "米/分钟，甲", (sols[0] + 10) * 60 / 1000, "千米/小时 → D；乙的速度换算为", sols[0] * 60 / 1000, "千米/小时（C）")

# 第60题：枚举类别与数量
P = ["贾", "易", "白", "单"]
T = ["雏鹰", "精英", "综合"]
ok = []
for ty in itertools.product(T, repeat=4):
    for n in itertools.product([1, 2, 3], repeat=4):
        t, c = dict(zip(P, ty)), dict(zip(P, n))
        if t["贾"] == t["单"] or c["贾"] == c["单"]:
            continue
        if n.count(1) != 1 or n.count(2) != 2:
            continue
        if t["白"] != "综合" or c["白"] != 3:
            continue
        if set(ty) != set(T) or t["易"] != "雏鹰" or t["单"] != "雏鹰":
            continue
        ok.append((t, c))
opts = {"A": lambda t, c: c["易"] == 2, "B": lambda t, c: t["贾"] == t["白"],
        "C": lambda t, c: any(t[p] == t["白"] or c[p] == c["白"] for p in P if p != "白"),
        "D": lambda t, c: t["单"] == "雏鹰" and c["单"] == 2}
print("第60题：满足条件的情形", len(ok), "种；一定为真：", [k for k, f in opts.items() if all(f(*s) for s in ok)])
