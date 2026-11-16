# -*- coding: utf-8 -*-
"""M02 资料分析第4组（第86—90题）：2019—2024年1—11月中国箱包及类似容器出口。

从 M02/输入/data.json 解析图1（数量）、图2（金额）的转写表，按材料数据精确计算，并核对增速与绝对量。
运行：python3 -B 本文件
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
D = json.loads((ROOT / "输入" / "data.json").read_text(encoding="utf-8"))
MAT = next(m for m in D["materials"] if m["id"] == "gd-mock-2026h2-s17-m4")
T1, T2 = MAT["blocks"]
assert T1["title"].startswith("图1") and "出口数量" in T1["title"]
assert T2["title"].startswith("图2") and "出口金额" in T2["title"]
assert "万吨" in T1["headers"][1] and "百万美元" in T2["headers"][1]


def num(s):
    return float(str(s).replace("−", "-"))


def key(s):
    return 2024.11 if "1—11" in s else int(s[:4])


Q = {key(r[0]): (num(r[1]), num(r[2]) / 100) for r in T1["rows"]}     # 万吨, 增速
V = {key(r[0]): (num(r[1]), num(r[2]) / 100) for r in T2["rows"]}     # 百万美元, 增速
YRS = [2019, 2020, 2021, 2022, 2023]

print("=== 数据自洽检查 ===")
for name, S in (("数量", Q), ("金额", V)):
    for y in YRS[1:]:
        calc = S[y][0] / S[y - 1][0] - 1
        ok = abs(round(calc * 100, 1) - S[y][1] * 100) <= 0.15
        print(f"{name}{y}: 算得{calc:+.3%} 表中{S[y][1]:+.1%} {'OK' if ok else '<<不符'}")
q23_11 = Q[2024.11][0] / (1 + Q[2024.11][1])
v23_11 = V[2024.11][0] / (1 + V[2024.11][1])
print(f"由2024年1—11月倒推2023年1—11月：数量 {q23_11:.2f} 万吨（<2023全年{Q[2023][0]}）；"
      f"金额 {v23_11:.1f} 百万美元（<2023全年{V[2023][0]}）")
assert q23_11 < Q[2023][0] and v23_11 < V[2023][0]

print("\n=== 第86题 2020—2023年出口总金额 ===")
s = sum(V[y][0] for y in (2020, 2021, 2022, 2023))
print(f"20639.5+27862.4+35570.6+35737.4 = {s:.1f} 百万美元 = {s / 100:.2f} 亿美元")

print("\n=== 第87题 2024年全年（12月按1—11月月均）比上年 ===")
v24 = V[2024.11][0] * 12 / 11
print(f"2024年全年 = 31373.1×12÷11 = {v24:.2f}；÷35737.4−1 = {v24 / V[2023][0] - 1:+.3%}")

print("\n=== 第88题 2019—2022年出口单价同比增速 ===")
pg = {}
for y in (2019, 2020, 2021, 2022):
    pg[y] = (1 + V[y][1]) / (1 + Q[y][1]) - 1
    extra = ""
    if y > 2019:
        exact = (V[y][0] / Q[y][0]) / (V[y - 1][0] / Q[y - 1][0]) - 1
        extra = f"；用绝对量算 {exact:+.3%}"
    print(f"{y}: (1{V[y][1]:+.1%})÷(1{Q[y][1]:+.1%})−1 = {pg[y]:+.3%}{extra}")
print("由大到小:", sorted(pg, key=pg.get, reverse=True))

print("\n=== 第89题 2023年12月出口数量占当年比重 ===")
dec = Q[2023][0] - q23_11
print(f"2023年1—11月 = 331÷1.092 = {q23_11:.3f}；12月 = {dec:.3f} 万吨；占 {dec / Q[2023][0]:.3%}")

print("\n=== 第90题 逐项（选错误的） ===")
inc = {y: Q[y][0] - Q[y - 1][0] for y in (2020, 2021, 2022, 2023)}
print(f"A 2020—2023年数量增长量: {inc}，最多 {max(inc, key=inc.get)}")
p22, p23 = V[2022][0] / Q[2022][0], V[2023][0] / Q[2023][0]
print(f"B 单价 2022={p22 * 100:.1f}，2023={p23 * 100:.1f} 美元/吨（百万美元÷万吨×100）；2023{'低于' if p23 < p22 else '高于'}2022"
      f"；也可比增速：金额{V[2023][1]:+.1%} < 数量{Q[2023][1]:+.1%}")
avg = sum(Q[y][0] for y in YRS) / 5
print(f"C 2019—2023年年均数量 = {sum(Q[y][0] for y in YRS):.0f}÷5 = {avg:.1f} 万吨")
print(f"D 2023年1—11月金额 = 31373.1÷(1−2.8%) = {v23_11:.1f} 百万美元 = {v23_11 / 100:.2f} 亿美元（选项写“亿元”，单位不符）")
