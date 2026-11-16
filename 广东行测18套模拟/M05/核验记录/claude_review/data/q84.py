# -*- coding: utf-8 -*-
"""Q84 2023年除民营企业外的其他内资企业平均收益金额（盲解）。"""
import sys; sys.path.insert(0, __import__('os').path.dirname(__file__))
from blind_common import *

N = 84
d = find_in_text(N, r"内资企业发明专利产业化平均收益金额为([\d.]+)万元/件")
a = find_in_text(N, r"较内资企业整体平均水平高([\d.]+%)")
b = find_in_text(N, r"较其他内资企业高([\d.]+%)")
print("材料：内资", d, "民营较内资整体高", a, "较其他内资高", b)
opts = opt_vals(N)
f = lambda e: e["d"] * (1 + e["a"]) / (1 + e["b"])
c, lo, hi, near, ok, s = robust_nearest({"d": d, "a": a, "b": b}, f, opts, "其他内资")
print(s)
print("民营 = %s 万元/件" % fx(frac(d) * (1 + frac(a)), 3))
w1 = frac(d) / (1 + frac(b))
print("错法：内资整体/1.227 = %s → %s（陷阱 A）" % (fx(w1, 2), nearest(w1, opts)))
w2 = frac(d) * (1 + frac(a)) * (1 - frac(b))
print("错法：民营×(1-22.7%%) = %s → %s" % (fx(w2, 2), nearest(w2, opts)))
print("盲解答案：C")
