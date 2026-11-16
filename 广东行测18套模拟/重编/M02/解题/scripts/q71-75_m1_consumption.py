# -*- coding: utf-8 -*-
"""M02 资料分析第1组（第71—75题）：全国居民人均消费支出。

从 M02/输入/data.json 读材料（文字数据先断言确实出现在材料中，表格直接解析），按材料数据精确计算。
运行：python3 -B 本文件
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
D = json.loads((ROOT / "输入" / "data.json").read_text(encoding="utf-8"))
MAT = next(m for m in D["materials"] if m["id"] == "gd-mock-2026h2-s17-m1")
TEXT = MAT["blocks"][0]["text"]


def num(s):
    return float(str(s).replace("−", "-").replace("%", "").replace(",", ""))


for s in ("全国居民人均消费支出26796元，同比名义增长9.2%",
          "人均交通通信消费支出3652元，同比增长14.3%",
          "城镇居民人均消费支出32994元，同比增长8.6%",
          "农村居民人均消费支出18175元，同比增长9.3%"):
    assert s in TEXT, s
C23, gC = 26796, 0.092          # 全国居民人均消费支出及增速
T23, gT = 3652, 0.143           # 人均交通通信消费支出及增速
U23, gU = 32994, 0.086          # 城镇
R23, gR = 18175, 0.093          # 农村

t1 = MAT["blocks"][1]
assert t1["title"].startswith("2018—2023年全国居民人均消费支出占人均可支配收入的比例")
RATIO = {int(r[0]): num(r[1]) / 100 for r in t1["rows"]}
t2 = MAT["blocks"][2]
YEARS = [int(h[:4]) for h in t2["headers"][1:]]
CITY = {r[0]: dict(zip(YEARS, map(num, r[1:]))) for r in t2["rows"]}

print("=== 数据自洽检查 ===")
print(f"文字城镇2023={U23}，表中全国2023={CITY['全国'][2023]}")
assert abs(CITY["全国"][2023] - U23) < 1e-9
g = CITY["全国"][2023] / CITY["全国"][2022] - 1
print(f"表中全国城镇2023增速={g:.4%}（文字8.6%）")
assert round(g * 100, 1) == 8.6
print("比例表各年:", RATIO)

print("\n=== 第71题 2023年全国居民人均可支配收入 ===")
I23 = C23 / RATIO[2023]
print(f"26796÷68.3% = {I23:.2f} 元")
opts71 = {"A": 42509, "B": 39233, "C": 33488, "D": 29089}
best = min(opts71, key=lambda k: abs(opts71[k] - I23))
print("最接近选项:", best, opts71[best])

print("\n=== 第72题 2022年五口之家交通通信支出 ===")
T22 = T23 / (1 + gT)
print(f"2022年人均交通通信 = 3652÷1.143 = {T22:.3f} 元；×5 = {5 * T22:.2f} 元")
print(f"干扰：2023年×5 = {5 * T23}；2022年×4 = {4 * T22:.1f}；人均 = {T22:.1f}")
opts72 = {"A": 15976, "B": 18260, "C": 12780, "D": 3195}
print("最接近选项:", min(opts72, key=lambda k: abs(opts72[k] - 5 * T22)))

print("\n=== 第73题 2023年全国居民人均可支配收入增速 ===")
C22 = C23 / (1 + gC)
I22 = C22 / RATIO[2022]
gI = I23 / I22 - 1
print(f"2022年消费 = 26796÷1.092 = {C22:.2f}；2022年收入 = {C22:.2f}÷66.5% = {I22:.2f}")
print(f"收入增速 = {I23:.2f}÷{I22:.2f}−1 = {gI:.4%}")
print(f"公式：(1+9.2%)×66.5%÷68.3%−1 = {(1 + gC) * RATIO[2022] / RATIO[2023] - 1:.4%}")
opts73 = {"A": 12.8, "B": 9.2, "C": 6.3, "D": 5.1}
print("最接近选项:", min(opts73, key=lambda k: abs(opts73[k] - gI * 100)))
lo = (1 + gC) * (RATIO[2022] - 0.0005) / (RATIO[2023] + 0.0005) - 1
hi = (1 + gC) * (RATIO[2022] + 0.0005) / (RATIO[2023] - 0.0005) - 1
print(f"比例按四舍五入区间计算，收入增速在 {lo:.3%} ~ {hi:.3%} 之间")

print("\n=== 第74题 上海城镇居民人均消费支出增速>10%的年份 ===")
sh = CITY["上海"]
cnt = 0
for y in range(2019, 2024):
    r = sh[y] / sh[y - 1] - 1
    flag = r > 0.10
    cnt += flag
    print(f"{y}: {sh[y]:.2f}/{sh[y-1]:.2f}−1 = {r:+.3%} {'>10%' if flag else ''}")
print("个数:", cnt)

print("\n=== 第75题 逐项 ===")
print(f"A 农村月均 = 18175÷12 = {R23 / 12:.1f} 元（说约2000元）")
down = [y for y in range(2019, 2024) if RATIO[y] < RATIO[y - 1]]
print(f"B 比例下降（消费增速<收入增速）的年份: {down}，共{len(down)}个（说2个）")
for y in YEARS:
    print(f"C {y}: 山东 {CITY['山东'][y]:.2f} vs 全国 {CITY['全国'][y]:.2f} -> {'低于' if CITY['山东'][y] < CITY['全国'][y] else '不低于'}")
dsh = sh[2023] - sh[2022]
dgd = CITY["广东"][2023] - CITY["广东"][2022]
print(f"D 上海增量 = {dsh:.2f}，广东增量 = {dgd:.2f}，倍数 = {dsh / dgd:.4f}；广东×3 = {3 * dgd:.2f}")
