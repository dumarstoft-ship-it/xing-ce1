# -*- coding: utf-8 -*-
"""Q86 2024年全国城市人均供水量（盲解）。人口 = 道路面积/人均道路面积。"""
import sys; sys.path.insert(0, __import__('os').path.dirname(__file__))
from blind_common import *

N = 86
area = find_in_text(N, r"城市道路面积([\d.]+)亿平方米")
per = find_in_text(N, r"人均道路面积([\d.]+)平方米")
dper = find_in_text(N, r"比上年增加([\d.]+)平方米")
gar = find_in_text(N, r"城市道路面积[\d.]+亿平方米，同比增长([\d.]+)％")
water = find_in_text(N, r"城市供水总量([\d.]+)亿立方米")
print("材料：道路面积", area, "亿㎡；人均道路面积", per, "㎡；供水总量", water, "亿m³")
opts = opt_vals(N)
f = lambda e: e["w"] / (e["a"] / e["p"])
c, lo, hi, near, ok, s = robust_nearest({"w": water, "a": area, "p": per}, f, opts, "人均供水量(m³)")
print(s)
print("城市人口 = %s 亿人" % fx(frac(area) / frac(per), 4))
# 常见错法
pop23 = (frac(area) / (1 + frac(gar) / 100)) / (frac(per) - frac(dper))
print("错法：用2023年人口(%s亿) → %s → %s" % (fx(pop23, 4), fx(frac(water) / pop23, 2), nearest(frac(water) / pop23, opts)))
print("各选项对应人口（亿人）：", {k: fx(frac(water) / v, 3) for k, v in opts.items()})
print("盲解答案：C")
