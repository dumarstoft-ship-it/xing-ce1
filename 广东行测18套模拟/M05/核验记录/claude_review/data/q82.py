# -*- coding: utf-8 -*-
"""Q82 若2022年较上年增长2.9%，2023年较两年前约增长（盲解）。"""
import sys; sys.path.insert(0, __import__('os').path.dirname(__file__))
from blind_common import *

N = 82
g23 = find_in_text(N, r"万元/件，较上年增长([\d.]+%)")
g22 = F(29, 1000)  # 题干假设值，精确
opts = opt_vals(N)
c, lo, hi, near, ok, s = robust_nearest({"g23": g23}, lambda e: (1 + g22) * (1 + e["g23"]) - 1, opts, "间隔增速")
print(s)
print("精确：(1+2.9%%)(1+%s)-1 = %s" % (g23, pct(c, 4)))
print("错法：直接相加 2.9%+3.8% = 6.7% → B（陷阱）")
print("盲解答案：C")
