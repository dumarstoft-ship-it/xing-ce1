# -*- coding: utf-8 -*-
"""Q80 能够从上述资料中推出的是（盲解）。"""
import sys; sys.path.insert(0, __import__('os').path.dirname(__file__))
from blind_common import *

N = 80
hdr, T = table_dict(N)
tot, io, car, rail = T["监管运输工具总数"], T["监管进出境总数"], T["其中：进出境汽车"], T["进出境火车"]

# A：2023年9月 进出境汽车 / 监管运输工具进出境总数（= 表中"监管进出境总数"行）
car23 = frac(car[2]) - frac(car[3])
io23 = frac(io[2]) - frac(io[3])
tot23 = frac(tot[2]) - frac(tot[3])
print("A：2023年9月 汽车=%s，进出境总数=%s，占比=%s（<80%%? %s）" % (car23, io23, pct(car23 / io23, 3), car23 / io23 < F(4, 5)))
print("   若误用'监管运输工具总数'行(%s)作分母：占比=%s（<80%% → 误判为正确！陷阱/歧义点）" % (tot23, pct(car23 / tot23, 3)))
print("   若误用2024年9月：%s" % pct(frac(car[2]) / frac(io[2]), 3))

# B：2024年1-8月 运输工具总数同比增长（增量）= 1-9月增量 - 9月增量
inc18 = frac(tot[5]) - frac(tot[3])
print("B：1-8月同比增量=%s-%s=%s 辆艘（%s 万）<700万? %s" % (tot[5], tot[3], inc18, fx(inc18 / 10000, 4), inc18 < 7000000))

# C：贡献率 = 火车9月增量 / 运输工具总数9月增量
cr = frac(rail[3]) / frac(tot[3])
print("C：火车9月增量/运输工具总数9月增量 = %s/%s = %s（>7%%? %s）" % (rail[3], tot[3], pct(cr, 3), cr > F(7, 100)))
cr2 = frac(rail[3]) / frac(io[3])
print("   若误用进出境总数增量为分母：%s（>7%% → 误判，陷阱）" % pct(cr2, 3))

# D：2024年1-9月 非进出境 = 运输工具总数 - 进出境总数
non = frac(tot[4]) - frac(io[4])
print("D：%s-%s=%s 辆艘 = %s 万（>243万? %s；超出阈值 %s 辆艘）" % (tot[4], io[4], non, fx(non / 10000, 4), non > 2430000, non - 2430000))
print("   D 的稳健性：表值为整数计数（非舍入显示值），按材料精确为真；但余量仅 %s/%s = %s，" % (non - 2430000, non, pct((non - 2430000) / non, 4)))
print("   需在第二阶段核对源表两数字是否逐位一致（任一数字抄错>122就会翻转）")
# 估算法敏感性
print("   估算：3190万-2947万=243万（四舍五入到万恰好相等），需精确减法才能判定'超过'")
print("盲解答案：D")
