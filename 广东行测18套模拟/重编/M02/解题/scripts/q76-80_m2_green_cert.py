# -*- coding: utf-8 -*-
"""M02 资料分析第2组（第76—80题）：绿证与绿色电力交易、售电公司、新型储能。

材料是纯文字。所用数据先断言确实出现在材料文字中，再计算。
运行：python3 -B 本文件
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
D = json.loads((ROOT / "输入" / "data.json").read_text(encoding="utf-8"))
MAT = next(m for m in D["materials"] if m["id"] == "gd-mock-2026h2-s17-m2")
TEXT = MAT["blocks"][0]["text"]


def has(s):
    assert s in TEXT, s
    return True


has("2024年全国完成绿证交易4.46亿个，同比增长364%")
has("绿证单独交易2.77亿个，绿色电力交易绿证1.69亿个")
has("跨省绿证单独交易达2.56亿个，约占单独交易总量的92.32%")
has("省内绿色电力交易绿证达1.52亿个，约占绿色电力交易绿证总量的89.64%")
TOTAL, SOLO, GP = 4.46, 2.77, 1.69
SOLO_X, SOLO_X_P = 2.56, 0.9232      # 单独交易中跨省
GP_IN, GP_IN_P = 1.52, 0.8964        # 绿电交易中省内

print("=== 数据自洽检查 ===")
print(f"单独+绿电 = {SOLO + GP:.2f}（合计4.46）")
print(f"2.56÷2.77 = {SOLO_X / SOLO:.4%}（材料92.32%；2.555~2.565÷2.765~2.775 的范围 "
      f"{2.555 / 2.775:.2%}~{2.565 / 2.765:.2%}，在舍入误差内）")
print(f"1.52÷1.69 = {GP_IN / GP:.4%}（材料89.64%；范围 {1.515 / 1.695:.2%}~{1.525 / 1.685:.2%}，在舍入误差内）")
has("2023年累计达697亿千瓦时")
has("累计完成绿色电力交易电量2336亿千瓦时，同比增长235.2％")
has("国家电网经营区累计绿色电力交易电量1358亿千瓦时")
has("南方电网经营区累计绿色电力交易电量221亿千瓦时")
has("蒙西电网经营区累计绿色电力交易电量757亿千瓦时")
E23, E24, gE = 697, 2336, 2.352
print(f"2336÷697−1 = {E24 / E23 - 1:.4%}（材料235.2%）")
print(f"三个经营区之和 = {1358 + 221 + 757}（合计2336）")
has("售电公司数从1889家增长到2613家")
has("所代理的零售用户数从31.76万增长到65.35万")
has("售电公司平均代理零售用户数约为250个")
print(f"65.35万÷2613 = {653500 / 2613:.1f} 个（材料约250个）")
print(f"2023年绿证交易 = 4.46÷4.64 = {TOTAL / 4.64:.3f} 亿个")

print("\n=== 第76题 绿证交易结构 ===")
gp_x = GP - GP_IN
solo_in = SOLO - SOLO_X
cross = SOLO_X + gp_x
inside = solo_in + GP_IN
print(f"绿电交易中跨省 = 1.69−1.52 = {gp_x:.2f}；单独交易中省内 = 2.77−2.56 = {solo_in:.2f}")
print(f"A 跨省合计 = 2.56+{gp_x:.2f} = {cross:.2f}，占全国 {cross / TOTAL:.3%}（只算单独交易跨省：{SOLO_X / TOTAL:.3%}）")
print(f"  按百分比口径：{SOLO * SOLO_X_P + GP * (1 - GP_IN_P):.4f}÷4.46 = {(SOLO * SOLO_X_P + GP * (1 - GP_IN_P)) / TOTAL:.3%}")
print(f"B 省内合计 = {solo_in:.2f}+1.52 = {inside:.2f}，绿电占 {GP_IN / inside:.3%}")
print(f"  按百分比口径：{GP * GP_IN_P:.4f}÷({GP * GP_IN_P:.4f}+{SOLO * (1 - SOLO_X_P):.4f}) = "
      f"{GP * GP_IN_P / (GP * GP_IN_P + SOLO * (1 - SOLO_X_P)):.3%}")
print(f"C 单独交易中跨省 {SOLO_X_P:.2%} vs 绿电交易中省内 {GP_IN_P:.2%}：前者{'低于' if SOLO_X_P < GP_IN_P else '高于'}后者")
print(f"D 绿电交易中省内 {GP_IN_P:.2%} vs 跨省 {1 - GP_IN_P:.2%}")

print("\n=== 第77题 2021—2024年年均增速（3年） ===")
items = {"售电公司数": (1889, 2613), "零售用户数": (31.76, 65.35), "零售交易电量": (2.41, 3.66)}
has("零售市场交易电量从2.41万亿千瓦时增长到3.66万亿千瓦时")
res = {}
for k, (a, b) in items.items():
    res[k] = (b / a) ** (1 / 3) - 1
    print(f"{k}: {b}÷{a} = {b / a:.4f}，年均 {res[k]:.3%}")
print("由高到低:", sorted(res, key=res.get, reverse=True))

print("\n=== 第78题 2024年绿电交易电量是2023年的倍数 ===")
print(f"2336÷697 = {E24 / E23:.4f}；1+235.2% = {1 + gE:.3f}")
opts78 = {"A": 2.0, "B": 3.2, "C": 3.4, "D": 3.9}
print("最接近选项:", min(opts78, key=lambda k: abs(opts78[k] - E24 / E23)),
      {k: round(abs(v - E24 / E23), 3) for k, v in opts78.items()})

print("\n=== 第79题 ===")
has("呈现“政策框架统一、区域差异化探索、技术多元化应用”的特征")
print("材料列出的特征：政策框架统一、区域差异化探索、技术多元化应用；“交易主体单一化”未出现：",
      "交易主体单一化" not in TEXT)

print("\n=== 第80题 ===")
has("内蒙古自治区出售绿证规模最大、达8041万个，浙江省购买绿证规模最大、达7622万个")
has("继国家电网、南方电网之后，蒙西电网获批复同意开展绿色电力交易，标志着绿色电力交易实现全覆盖")
has("甘肃储能以“报量不报价”方式参与现货")
print("A 出售最大的是内蒙古，浙江是购买最大 → 错")
print("B 蒙西电网也已开展，实现全覆盖 → 错")
print(f"C 蒙西经营区757 {'>' if 757 > 1358 else '<'} 国家电网经营区1358 → 错")
print("D 甘肃储能以“报量不报价”方式参与现货 → 对")
