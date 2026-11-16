# -*- coding: utf-8 -*-
"""Q81 若保持2023年同比增速不变，2024年企业发明专利产业化平均收益金额（盲解）。"""
import sys; sys.path.insert(0, __import__('os').path.dirname(__file__))
from blind_common import *

N = 81
v = find_in_text(N, r"企业发明专利产业化平均收益金额为([\d.]+)万元/件")
g = find_in_text(N, r"万元/件，较上年增长([\d.]+%)")
print("材料：2023 =", v, "万元/件，增速", g)
opts = opt_vals(N)
c, lo, hi, near, ok, s = robust_nearest({"v": v, "g": g}, lambda e: e["v"] * (1 + e["g"]), opts, "2024预测值")
print(s)
print("错法：v/(1-g)=%s → %s；v×(1+2g)=%s → %s" % (
    fx(frac(v) / (1 - frac(g)), 2), nearest(frac(v) / (1 - frac(g)), opts),
    fx(frac(v) * (1 + 2 * frac(g)), 2), nearest(frac(v) * (1 + 2 * frac(g)), opts)))
print("盲解答案：A")
