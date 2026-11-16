# -*- coding: utf-8 -*-
"""Q83 2023年港澳台投资企业比外商投资企业平均收益金额高/低多少（盲解）。"""
import sys; sys.path.insert(0, __import__('os').path.dirname(__file__))
from blind_common import *

N = 83
d = find_in_text(N, r"内资企业发明专利产业化平均收益金额为([\d.]+)万元/件")
a = find_in_text(N, r"分别较港澳台投资企业以及外商投资企业低([\d.]+%)和")
b = find_in_text(N, r"分别较港澳台投资企业以及外商投资企业低[\d.]+%和([\d.]+%)")
print("材料：内资", d, "较港澳台低", a, "较外商低", b)
f = lambda e: e["d"] / (1 - e["a"]) - e["d"] / (1 - e["b"])
c, lo, hi, _ = corners({"d": d, "a": a, "b": b}, f)
gat = frac(d) / (1 - frac(a)); wz = frac(d) / (1 - frac(b))
print("港澳台=%s，外商=%s，差=%s 万元/件（区间[%s,%s]）" % (fx(gat, 2), fx(wz, 2), fx(c, 2), fx(lo, 2), fx(hi, 2)))
def cls(x):
    if x < 0:
        return "B 低70万元/件以上" if x < -70 else "A 低不到70万元/件"
    return "D 高70万元/件以上" if x > 70 else "C 高不到70万元/件"
print("判定：", cls(c), "| 端点", cls(lo), cls(hi))
w = frac(d) * (1 + frac(a)) - frac(d) * (1 + frac(b))
print("错法：用 内资×(1+r) 求港澳台/外商 → 差=%s → %s（陷阱 A）" % (fx(w, 2), cls(w)))
print("盲解答案：B")
