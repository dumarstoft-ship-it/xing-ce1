# -*- coding: utf-8 -*-
"""Q87 截至2023年末全国城市排水管道长度（盲解）。"""
import sys; sys.path.insert(0, __import__('os').path.dirname(__file__))
from blind_common import *

N = 87
v = find_in_text(N, r"排水管道长度([\d.]+)万公里")
g = find_in_text(N, r"排水管道长度[\d.]+万公里，同比增长([\d.]+)％")
print("材料：2024末排水管道", v, "万公里，增速", g, "%")
opts = opt_vals(N)
c, lo, hi, near, ok, s = robust_nearest({"v": v, "g": (frac(g) / 100, half_unit(g) / 100)},
                                        lambda e: e["v"] / (1 + e["g"]), opts, "2023末排水管道(万公里)")
print(s)
w = frac(v) * (1 - frac(g) / 100)
print("错法：v×(1-g)=%s → %s（同样落在 A）" % (fx(w, 3), nearest(w, opts)))
sup = frac(find_in_text(N, r"供水管道长度([\d.]+)万公里")); gs = frac(find_in_text(N, r"供水管道长度[\d.]+万公里，同比增长([\d.]+)％"))
print("错法：错看成供水管道 → %s → %s" % (fx(sup / (1 + gs / 100), 2), nearest(sup / (1 + gs / 100), opts)))
print("盲解答案：A")
