# -*- coding: utf-8 -*-
"""Q88 2022-2024年平均每个正在建设轨道交通的城市在建线路长度趋势（盲解）。"""
import sys; sys.path.insert(0, __import__('os').path.dirname(__file__))
from blind_common import *

N = 88
hdr, T = table_dict(N)
print("表头：", hdr)
vals = {}
for y in ["2021", "2022", "2023", "2024"]:
    L, n = T[y][4], T[y][3]
    c, lo, hi, _ = corners({"L": L, "n": (frac(n), F(0))}, lambda e: e["L"] / e["n"])
    vals[y] = (c, lo, hi)
    print("%s：%s/%s = %s 公里/城（区间[%s,%s]）" % (y, L, n, fx(c, 3), fx(lo, 3), fx(hi, 3)))
a, b, c = vals["2022"][0], vals["2023"][0], vals["2024"][0]
trend = ("先升后降" if b > a and c < b else "先降后升" if b < a and c > b else "逐年上升" if a < b < c else "逐年下降" if a > b > c else "?")
print("2022→2023→2024：", trend, "（区间不重叠，稳健）")
print("错法：只看在建线路长度 4802.89→5061.32→4121.13 也是先升后降；看在建城市数 44→45→38 也是先升后降（陷阱不区分）")
print("错法：误用已建成：", [fx(frac(T[y][2]) / frac(T[y][1]), 2) for y in ["2022", "2023", "2024"]])
print("盲解答案：D")
