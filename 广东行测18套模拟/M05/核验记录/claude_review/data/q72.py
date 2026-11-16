# -*- coding: utf-8 -*-
"""Q72 2022年全国城镇居民国内出游花费约比农村居民多几倍（盲解）。"""
import sys; sys.path.insert(0, __import__('os').path.dirname(__file__))
from blind_common import *

N = 72
u23 = find_in_text(N, r"城镇居民国内出游花费([\d.]+)万亿元")
gu = find_in_text(N, r"城镇居民国内出游花费[\d.]+万亿元，同比增长([\d.]+%)")
r23 = find_in_text(N, r"农村居民国内出游花费([\d.]+)万亿元")
gr = find_in_text(N, r"农村居民国内出游花费[\d.]+万亿元，同比增长([\d.]+%)")
tot23 = find_in_text(N, r"国内游客出游总花费([\d.]+)万亿元")
gt = find_in_text(N, r"国内游客出游总花费[\d.]+万亿元，同比增长([\d.]+%)")
print("材料：城镇", u23, gu, "农村", r23, gr, "总", tot23, gt)
opts = opt_vals(N)
print("选项：", {k: str(v) for k, v in opts.items()})

# 正确：2022城镇/2022农村 - 1（多几倍 = 倍数 - 1）
f = lambda e: (e["u"] / (1 + e["gu"])) / (e["r"] / (1 + e["gr"])) - 1
c, lo, hi, near, ok, s = robust_nearest({"u": u23, "gu": gu, "r": r23, "gr": gr}, f, opts, "多几倍")
print(s)
print("  2022城镇=%s万亿元，2022农村=%s万亿元，是几倍=%s" % (
    fx(frac(u23) / (1 + frac(gu)), 5), fx(frac(r23) / (1 + frac(gr)), 5), fx(c + 1, 5)))
# 备选：2022农村 = 2022总 - 2022城镇
alt = (frac(u23) / (1 + frac(gu))) / (frac(tot23) / (1 + frac(gt)) - frac(u23) / (1 + frac(gu))) - 1
print("备选算法（农村=总-城镇）：多 %s 倍 -> 最接近 %s" % (fx(alt, 4), nearest(alt, opts)))
print("错法：把'多几倍'当'是几倍' -> %s -> %s（B 为陷阱）" % (fx(c + 1, 4), nearest(c + 1, opts)))
print("错法：直接用2023年 4.2/0.7=6 倍 -> 是6倍/多5倍 -> C 或 B")
print("盲解答案：A")
