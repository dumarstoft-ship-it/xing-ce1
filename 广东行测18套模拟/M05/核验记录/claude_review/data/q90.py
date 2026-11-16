# -*- coding: utf-8 -*-
"""Q90 2021-2024年全国城市新建成轨道交通线路长度同比增量变化趋势（盲解）。
累计建成(已建成线路长度) → 一次差分 = 当年新建成 → 二次差分 = 新建成同比增量；与选项图点位（q90_points.json）对照。"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from blind_common import *

N = 90
hdr, T = table_dict(N)
yrs = [str(y) for y in range(2018, 2025)]
cum = {y: frac(T[y][2]) for y in yrs}
new = {yrs[i]: cum[yrs[i]] - cum[yrs[i - 1]] for i in range(1, len(yrs))}
dd = {yrs[i]: new[yrs[i]] - new[yrs[i - 1]] for i in range(2, len(yrs))}
print("已建成线路长度（累计）：", {y: T[y][2] for y in yrs})
print("当年新建成（一次差分）：", {y: fx(v, 2) for y, v in new.items()})
print("新建成同比增量（二次差分）：", {y: fx(v, 2) for y, v in dd.items()})
print("舍入：每个累计值 ±0.005 → 二次差分误差 ≤ ±0.02 公里，可忽略")

def norm(vals):
    lo, hi = min(vals), max(vals)
    return [float((v - lo) / (hi - lo)) for v in vals]

Y = ["2021", "2022", "2023", "2024"]
cands = {
    "正确：新建成同比增量(二次差分)": [dd[y] for y in Y],
    "错法1：新建成长度本身(一次差分)": [new[y] for y in Y],
    "错法2：新建成同比增速": [new[y] / new[str(int(y) - 1)] - 1 for y in Y],
    "错法3：已建成累计长度": [cum[y] for y in Y],
    "错法4：已建成累计同比增速": [cum[y] / cum[str(int(y) - 1)] - 1 for y in Y],
    "错法5：二次差分错位(2020-2023)": [dd[str(int(y) - 1)] for y in Y],
    "错法6：在建线路长度同比增量": [frac(T[y][4]) - frac(T[str(int(y) - 1)][4]) for y in Y],
}
pts = json.load(open(os.path.join(os.path.dirname(__file__), "q90_points.json")))
optn = {}
for k, v in pts.items():
    ys = [c[1] for c in v]
    lo, hi = max(ys), min(ys)
    optn[k] = [(lo - y) / (lo - hi) for y in ys]
print("\n选项图归一化高度：", {k: ["%.3f" % t for t in v] for k, v in optn.items()})
print("\n各算法归一化序列 与 各选项图的最大偏差（越小越吻合）：")
for name, vals in cands.items():
    nv = norm(vals)
    devs = {k: max(abs(a - b) for a, b in zip(nv, ov)) for k, ov in optn.items()}
    best = min(devs, key=devs.get)
    print("  %-30s %s | 偏差 %s → 最吻合 %s" % (name, ["%.3f" % t for t in nv],
          {k: "%.3f" % d for k, d in devs.items()}, best))
print("\n结论：正确序列 -738.46, 81.50, -218.30, -66.96（低→最高→回落→回升），形状与 D 吻合（归一化偏差<0.01）；"
      "A 对应只做一次差分（新建成长度本身）的错法。")
print("盲解答案：D")
