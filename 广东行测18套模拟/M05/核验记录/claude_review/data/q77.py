# -*- coding: utf-8 -*-
"""Q77 2024年1-9月监管进出境汽车、火车、船舶、飞机数量同比增速第二高（盲解）。"""
import sys; sys.path.insert(0, __import__('os').path.dirname(__file__))
from blind_common import *

N = 77
hdr, T = table_dict(N)
rows = {"汽车": "其中：进出境汽车", "火车": "进出境火车", "船舶": "进出境船舶", "飞机": "进出境飞机"}
g = {}
for k, r in rows.items():
    cur, inc = frac(T[r][4]), frac(T[r][5])
    g[k] = inc / (cur - inc)
    print("%s：1-9月 %s，增量 %s，上年同期 %s，增速 %s" % (k, T[r][4], T[r][5], cur - inc, pct(g[k], 2)))
rk = sorted(g, key=lambda k: g[k], reverse=True)
print("增速排序：", rk, "→ 第二高：", rk[1])
rk2 = sorted(rows, key=lambda k: frac(T[rows[k]][5]), reverse=True)
print("错法（比增量/把增长列当百分比直接比）：", rk2, "→ 第二：", rk2[1], "（A 火车，陷阱）")
print("9月单月增速（易混时段）：", {k: pct(frac(T[r][3]) / (frac(T[r][2]) - frac(T[r][3])), 2) for k, r in rows.items()})
print("盲解答案：B")
