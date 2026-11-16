# -*- coding: utf-8 -*-
"""M02 资料分析第3组（第81—85题）：2013—2023年我国汽车制造业。

从 M02/输入/data.json 解析表格，按材料数据精确计算；并用相邻年份绝对量核对表中各增速列。
运行：python3 -B 本文件
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
D = json.loads((ROOT / "输入" / "data.json").read_text(encoding="utf-8"))
MAT = next(m for m in D["materials"] if m["id"] == "gd-mock-2026h2-s17-m3")
T = MAT["blocks"][0]
assert T["title"] == "2013—2023年我国汽车制造业统计情况"
assert "企业亏损面" in MAT["blocks"][1]["text"]


def num(s):
    s = str(s).replace("−", "-")
    return None if s in ("—", "-", "") else float(s)


KEYS = ["企业数", "亏损企业数", "亏损总额", "亏损增速", "收入", "收入增速", "利润", "利润增速"]
ROWS = {int(r[0]): dict(zip(KEYS, map(num, r[1:]))) for r in T["rows"]}
Y = sorted(ROWS)

print("=== 数据自洽检查：相邻年份绝对量算出的增速 vs 表中增速 ===")
bad = []
for y in Y[1:]:
    for v, g in (("亏损总额", "亏损增速"), ("收入", "收入增速"), ("利润", "利润增速")):
        a, b, gg = ROWS[y - 1][v], ROWS[y][v], ROWS[y][g]
        if a is None or b is None or gg is None:
            continue
        calc = (b / a - 1) * 100
        ok = abs(round(calc, 1) - gg) <= 0.1
        if not ok:
            bad.append((y, v, calc, gg))
        print(f"{y} {v}: 算得{calc:+.2f}% 表中{gg:+.1f}% {'OK' if ok else '<<不符'}")
print("不符项:", bad or "无")
for y in Y:
    assert ROWS[y]["亏损企业数"] < ROWS[y]["企业数"]

print("\n=== 第81题 亏损面 2022 vs 2016 ===")
lr = {y: ROWS[y]["亏损企业数"] / ROWS[y]["企业数"] for y in Y}
for y in Y:
    print(f"{y}: {ROWS[y]['亏损企业数']:.0f}/{ROWS[y]['企业数']:.0f} = {lr[y]:.4%}")
print(f"2022−2016 = {(lr[2022] - lr[2016]) * 100:+.3f} 个百分点")

print("\n=== 第82题 2013—2023年年均增长（10年） ===")
for k in ("利润", "亏损总额", "亏损企业数", "企业数"):
    ratio = ROWS[2023][k] / ROWS[2013][k]
    print(f"{k}: {ROWS[2023][k]}÷{ROWS[2013][k]} = {ratio:.4f}，年均 {ratio ** 0.1 - 1:+.3%}")

print("\n=== 第83题 2013—2018年主营业务利润率同比上升的年份 ===")
# 2012年由2013年增速倒推
inc12 = ROWS[2013]["收入"] / (1 + ROWS[2013]["收入增速"] / 100)
pro12 = ROWS[2013]["利润"] / (1 + ROWS[2013]["利润增速"] / 100)
margin = {2012: pro12 / inc12}
for y in range(2013, 2019):
    margin[y] = ROWS[y]["利润"] / ROWS[y]["收入"]
up = []
for y in range(2013, 2019):
    gp, gi = ROWS[y]["利润增速"], ROWS[y]["收入增速"]
    flag = margin[y] > margin[y - 1]
    assert flag == (gp > gi)
    up += [y] if flag else []
    print(f"{y}: 利润率 {margin[y]:.4%}（上年 {margin[y-1]:.4%}）；利润增速{gp:+.1f}% vs 收入增速{gi:+.1f}% -> {'上升' if flag else '下降'}")
print("上升年份:", up, "共", len(up), "个；若不计2013年则", len([y for y in up if y > 2013]), "个")

print("\n=== 第84题 2022年平均每家亏损企业亏损额的同比变化 ===")
per = {y: ROWS[y]["亏损总额"] * 1e4 / ROWS[y]["亏损企业数"] for y in (2021, 2022)}   # 万元
for y in per:
    print(f"{y}: {ROWS[y]['亏损总额']}亿元÷{ROWS[y]['亏损企业数']:.0f} = {per[y]:.2f} 万元")
print(f"变化 = {per[2022] - per[2021]:+.2f} 万元")

print("\n=== 第85题 ===")
s13 = {y: ROWS[y]["亏损总额"] for y in range(2016, 2021)}
mx, mn = max(s13, key=s13.get), min(s13, key=s13.get)
print(f"① 十三五（2016—2020）亏损总额：{s13}；最多{mx}年{s13[mx]}，最少{mn}年{s13[mn]}，倍数 {s13[mx] / s13[mn]:.4f}")
d13 = ROWS[2013]["利润"] - pro12
print(f"② 2013年利润增量 = 5107.7−5107.7÷1.256 = {d13:.2f} 亿元")
print(f"③ 表中只有年度数据；2023年全年亏损总额增量 = {ROWS[2023]['亏损总额'] - ROWS[2022]['亏损总额']:.1f} 亿元（不是12月当月数据）")
