# -*- coding: utf-8 -*-
"""Q73 2023年全国城镇居民国内平均每人次出游花费与上年相比（盲解，含单位核对）。"""
import sys; sys.path.insert(0, __import__('os').path.dirname(__file__))
from blind_common import *

N = 73
txt = material_text(N)
pu = find_in_text(N, r"城镇居民国内出游([\d.]+)亿人次")
gpu = find_in_text(N, r"城镇居民国内出游[\d.]+亿人次，同比增长([\d.]+%)")
su = find_in_text(N, r"城镇居民国内出游花费([\d.]+)万亿元")
gsu = find_in_text(N, r"城镇居民国内出游花费[\d.]+万亿元，同比增长([\d.]+%)")
print("材料：城镇人次", pu, "亿人次", gpu, "；城镇花费", su, "万亿元", gsu)
print("单位：万亿元/亿人次 = 10^12/10^8 元/人次 = 10^4 元/人次")
K = 10000  # 万亿元/亿人次 -> 元/人次

def inc(e):
    a23 = e["su"] / e["pu"] * K
    a22 = (e["su"] / (1 + e["gsu"])) / (e["pu"] / (1 + e["gpu"])) * K
    return a23 - a22

c, lo, hi, _ = corners({"su": su, "pu": pu, "gsu": gsu, "gpu": gpu}, inc)
a23 = frac(su) / frac(pu) * K
a22 = (frac(su) / (1 + frac(gsu))) / (frac(pu) / (1 + frac(gpu))) * K
print("2023城镇人均 = %s 元；2022城镇人均 = %s 元；增量 = %s 元；增速 = %s" % (
    fx(a23, 2), fx(a22, 2), fx(c, 2), pct(a23 / a22 - 1)))
print("舍入区间：增量 ∈ [%s, %s] 元" % (fx(lo, 2), fx(hi, 2)))

def cls(x):
    if x > 0:
        return "D 上升100元以上" if x > 100 else "C 上升不到100元"
    return "B 下降100元以上" if x < -100 else "A 下降不到100元"
print("判定：", cls(c), "| 端点", cls(lo), cls(hi))
print("单位误读检验：若把 4.2万亿元/37.6亿人次 误当 万元/人次 ×1 → 0.1117 万元=1117元，结论不变；"
      "若误用 10^3 换算（4.2万亿/37.6亿≈111.7元）则增量≈23.7元 → C（单位陷阱）")
print("增量(若错用×10^3)=", fx(c / 10, 2), "->", cls(c / 10))
print("盲解答案：D")
