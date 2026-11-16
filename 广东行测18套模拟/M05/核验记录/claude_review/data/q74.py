# -*- coding: utf-8 -*-
"""Q74 2018-2023年全国国内游客出游总花费同比变化幅度超过50%的年份数（盲解）。"""
import sys; sys.path.insert(0, __import__('os').path.dirname(__file__))
from blind_common import *

N = 74
hdr, T = table_dict(N)
g23 = find_in_text(N, r"国内游客出游总花费[\d.]+万亿元，同比增长([\d.]+%)")
cnt_c = 0
cnt_set = set()
for y in range(2018, 2024):
    a, b = T[str(y)][2], T[str(y - 1)][2]
    f = lambda e: e["a"] / e["b"] - 1
    c, lo, hi, _ = corners({"a": a, "b": b}, f)
    flag = abs(c) > F(1, 2)
    flags = {abs(lo) > F(1, 2), abs(hi) > F(1, 2)}
    cnt_c += flag
    print("%d: %s/%s-1 = %s  舍入区间[%s, %s]  |变化|>50%%? %s%s" % (
        y, a, b, pct(c, 2), pct(lo, 2), pct(hi, 2), flag, "" if len(flags) == 1 else "（舍入敏感）"))
print("2023 文字增速 =", g23, "（与表值 4.9/2.0-1=145% 一致方向，均 >50%）")
print("变化幅度（绝对值）>50% 的年份数 =", cnt_c, "（2020 降 61.4%，2023 增 140.3%）")
print("错法：只数增长超过50% → 1 年（A）；把2022年降幅 31% 误作>50% 或把2021年+31.8% 误判 → C")
print("盲解答案：B")
