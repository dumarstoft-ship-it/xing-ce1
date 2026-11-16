# -*- coding: utf-8 -*-
"""Q78 2024年9月绝对量小于当年1-8月月均量的指标（盲解）。条件：9月 < (1-9累计-9月)/8 ⟺ 9×9月 < 1-9累计。"""
import sys; sys.path.insert(0, __import__('os').path.dirname(__file__))
from blind_common import *

N = 78
hdr, T = table_dict(N)
rows = {"A 进口货运量": "监管进口货运量", "B 出口货运量": "监管出口货运量",
        "C 进出境船舶数量": "进出境船舶", "D 进出境飞机数量": "进出境飞机"}
for k, r in rows.items():
    sep, cum = frac(T[r][2]), frac(T[r][4])
    avg18 = (cum - sep) / 8
    print("%s：9月=%s，1-8月月均=%s，9月<月均? %s（差 %s）" % (k, sep, fx(avg18, 2), sep < avg18, fx(sep - avg18, 2)))
print("错法：与1-9月月均比（9月<1-9累计/9 等价，结论相同）；与1-9累计/8 比较则全部'小于'")
print("盲解答案：C")
