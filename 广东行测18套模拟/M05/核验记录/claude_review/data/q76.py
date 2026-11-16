# -*- coding: utf-8 -*-
"""Q76 2023年9月我国监管进出口货运量（盲解）。表中"同比增长"列数值无%，且量级（如7531496）不可能是百分比，按绝对增量处理。"""
import sys; sys.path.insert(0, __import__('os').path.dirname(__file__))
from blind_common import *

N = 76
hdr, T = table_dict(N)
print("表头：", hdr)
imp, exp_ = T["监管进口货运量"], T["监管出口货运量"]
print("进口：", imp, "\n出口：", exp_)
i23 = frac(imp[2]) - frac(imp[3])
e23 = frac(exp_[2]) - frac(exp_[3])
print("2023年9月 进口=%s 出口=%s 合计=%s 万吨（整数精确，无舍入问题）" % (i23, e23, i23 + e23))
opts = opt_vals(N)
print("选项：", {k: str(v) for k, v in opts.items()}, "→ 精确等于", [k for k, v in opts.items() if v == i23 + e23])
print("错法：出口减55（符号错）→", frac(imp[2]) + frac(exp_[2]) - frac(imp[3]) - abs(frac(exp_[3])), "= B")
print("错法：只算进口 →", i23, "≈ D 29830")
# 若误读为百分比
mi = frac(imp[2]) / (1 + frac(imp[3]) / 100)
me = frac(exp_[2]) / (1 + frac(exp_[3]) / 100)
print("误读为百分比：进口=%s 出口=%s 合计=%s（与任一选项都不接近，且1018%%增长不合常理）" % (fx(mi, 1), fx(me, 1), fx(mi + me, 1)))
print("盲解答案：A")
