# -*- coding: utf-8 -*-
"""Q71 2023年全国国内游客平均每人次出游花费与上年相比（盲解）。"""
import sys; sys.path.insert(0, __import__('os').path.dirname(__file__))
from blind_common import *

N = 71
txt = material_text(N)
g_trip = find_in_text(N, r"全国国内出游48\.9亿人次，同比增长([\d.]+%)")
g_spend = find_in_text(N, r"国内游客出游总花费4\.9万亿元，同比增长([\d.]+%)")
hdr, T = table_dict(N)
print("材料取值：人次增速", g_trip, "总花费增速", g_spend)
print("表：2022", T["2022"], "2023", T["2023"])

# 方法1：用文字增速（最精确）：人均花费增速 = (1+g花费)/(1+g人次) - 1
f1 = lambda e: (1 + e["gs"]) / (1 + e["gt"]) - 1
c, lo, hi, res = corners({"gs": g_spend, "gt": g_trip}, f1)
print("方法1 增速公式：中心 %s，舍入区间 [%s, %s]" % (pct(c), pct(lo), pct(hi)))

# 方法2：用表中2022、2023年数据直接算人均
f2 = lambda e: (e["s23"] / e["p23"]) / (e["s22"] / e["p22"]) - 1
c2, lo2, hi2, _ = corners({"s23": T["2023"][2], "p23": T["2023"][1], "s22": T["2022"][2], "p22": T["2022"][1]}, f2)
print("方法2 表值：中心 %s，舍入区间 [%s, %s]" % (pct(c2), pct(lo2), pct(hi2)))
print("人均花费 2023 = %s 元，2022 = %s 元（表值；万亿元/亿人次×10^4 = 元）" % (
    fx(frac(T["2023"][2]) / frac(T["2023"][1]) * 10000, 2), fx(frac(T["2022"][2]) / frac(T["2022"][1]) * 10000, 2)))

def cls(x):
    if x > 0:
        return "B 增长了20%以上" if x > F(1, 5) else "A 增长了不到20%"
    return "D 减少了20%以上" if x < -F(1, 5) else "C 减少了不到20%"
print("判定：方法1 中心/端点 ->", cls(c), cls(lo), cls(hi))
print("判定：方法2 中心/端点 ->", cls(c2), cls(lo2), cls(hi2))
print("错法：直接用 140.3%-93.3% = 47.0% 也落在 B；把人均算成 人次/花费 则反向（减少约19.6%→C）")
inv = (1 + frac(g_trip)) / (1 + frac(g_spend)) - 1
print("  人次/花费 倒置：", pct(inv), "->", cls(inv))
print("盲解答案：B")
