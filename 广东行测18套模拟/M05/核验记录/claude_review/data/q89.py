# -*- coding: utf-8 -*-
"""Q89 截至2024年末城市生活垃圾焚烧处理能力占无害化处理能力的比重同比变化（盲解）。"""
import sys; sys.path.insert(0, __import__('os').path.dirname(__file__))
from blind_common import *

N = 89
tot = find_in_text(N, r"生活垃圾无害化处理能力([\d.]+)万吨/日")
gt = find_in_text(N, r"生活垃圾无害化处理能力[\d.]+万吨/日，同比增长([\d.]+)％")
inc = find_in_text(N, r"焚烧处理能力([\d.]+)万吨/日")
gi = find_in_text(N, r"焚烧处理能力[\d.]+万吨/日，同比增长([\d.]+)%")
sh = find_in_text(N, r"占无害化处理能力的([\d.]+)％")
print("材料：无害化", tot, gt, "% ；焚烧", inc, gi, "% ；占比", sh, "%")
print("校核：焚烧/无害化 = %s（材料给 %s%%）" % (pct(frac(inc) / frac(tot), 3), sh))
spec = {"s": (frac(sh) / 100, half_unit(sh) / 100), "gi": (frac(gi) / 100, half_unit(gi) / 100), "gt": (frac(gt) / 100, half_unit(gt) / 100)}
f = lambda e: e["s"] - e["s"] * (1 + e["gt"]) / (1 + e["gi"])
c, lo, hi, _ = corners(spec, f)
print("2023年占比 = %s；变化 = %s 个百分点（区间[%s,%s]）" % (
    pct(frac(sh) / 100 * (1 + frac(gt) / 100) / (1 + frac(gi) / 100), 3), fx(c * 100, 3), fx(lo * 100, 3), fx(hi * 100, 3)))
def cls(x):
    x = x * 100
    if x > 0:
        return "B 上升1个百分点以上" if x > 1 else "A 上升不到1个百分点"
    return "D 下降1个百分点以上" if x < -1 else "C 下降不到1个百分点"
print("判定：", cls(c), "| 端点", cls(lo), cls(hi))
print("公式法：现期比重×(a-b)/(1+a) = 78.09%×(6.87%-3.05%)/(1+6.87%) = " + fx(frac(sh) * (frac(gi) - frac(gt)) / (100 + frac(gi)), 3) + " 个百分点")
print("盲解答案：B")
