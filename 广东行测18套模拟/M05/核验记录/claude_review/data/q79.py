# -*- coding: utf-8 -*-
"""Q79 2023年1-9月监管进口货运量约是出口货运量的多少倍（盲解）。"""
import sys; sys.path.insert(0, __import__('os').path.dirname(__file__))
from blind_common import *

N = 79
hdr, T = table_dict(N)
imp, exp_ = T["监管进口货运量"], T["监管出口货运量"]
i23 = frac(imp[4]) - frac(imp[5])
e23 = frac(exp_[4]) - frac(exp_[5])
r = i23 / e23
opts = opt_vals(N)
print("2023年1-9月 进口=%s 出口=%s 倍数=%s → 最接近 %s" % (i23, e23, fx(r, 5), nearest(r, opts)))
r24 = frac(imp[4]) / frac(exp_[4])
print("错法：用2024年1-9月 = %s → %s（与正确选项相同，陷阱不区分）" % (fx(r24, 5), nearest(r24, opts)))
i9, e9 = frac(imp[2]) - frac(imp[3]), frac(exp_[2]) - frac(exp_[3])
print("错法：用2023年9月单月 = %s → %s" % (fx(i9 / e9, 4), nearest(i9 / e9, opts)))
print("错法：用2024年9月单月 = %s → %s" % (fx(frac(imp[2]) / frac(exp_[2]), 4), nearest(frac(imp[2]) / frac(exp_[2]), opts)))
mp = (frac(imp[4]) / (1 + frac(imp[5]) / 100)) / (frac(exp_[4]) / (1 + frac(exp_[5]) / 100))
print("误读增长列为百分比 = %s → %s（数值荒谬：11001%%）" % (fx(mp, 4), nearest(mp, opts)))
print("各选项与正确值差：", {k: fx(v - r, 4) for k, v in opts.items()})
print("盲解答案：B")
