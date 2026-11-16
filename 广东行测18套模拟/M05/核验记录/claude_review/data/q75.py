# -*- coding: utf-8 -*-
"""Q75 能够从上述资料中推出的是（盲解）。"""
import sys; sys.path.insert(0, __import__('os').path.dirname(__file__))
from blind_common import *

N = 75
hdr, T = table_dict(N)
n_ts = find_in_text(N, r"全国共有旅行社(\d+)家")
rev = find_in_text(N, r"营业收入([\d.]+)亿元")
prof = find_in_text(N, r"营业利润([\d.]+)亿元")
gt = find_in_text(N, r"全国国内出游[\d.]+亿人次，同比增长([\d.]+%)")
gu = find_in_text(N, r"城镇居民国内出游[\d.]+亿人次，同比增长([\d.]+%)")
print("材料：旅行社", n_ts, "家；营业收入", rev, "亿元；营业利润", prof, "亿元；出游人次增速", gt, "城镇", gu)

# A
f = lambda e: e["p"] * 10 ** 8 / e["n"] / 10 ** 4  # 万元/家
c, lo, hi, _ = corners({"p": prof, "n": (frac(n_ts), F(0))}, f)
print("A：平均每家营业利润 = %s 万元（区间[%s,%s]）>60万元? %s" % (fx(c, 3), fx(lo, 3), fx(hi, 3), c > 60))
print("   错用营业收入：%s 万元/家（>60，陷阱）" % fx(frac(rev) * 10 ** 8 / frac(n_ts) / 10 ** 4, 1))

# B：农村占比变化 ⟺ 城镇占比反向；城镇增速 94.9% > 总增速 93.3% → 城镇占比升 → 农村占比降
print("B：城镇人次增速 %s > 全国 %s → 城镇占比上升、农村占比下降 → B 错" % (gu, gt))
pu = frac(find_in_text(N, r"城镇居民国内出游([\d.]+)亿人次"))
pt = frac(find_in_text(N, r"全国国内出游([\d.]+)亿人次"))
sh23 = (pt - pu) / pt
sh22 = (pt / (1 + frac(gt)) - pu / (1 + frac(gu))) / (pt / (1 + frac(gt)))
print("   农村占比 2023=%s，2022=%s" % (pct(sh23, 2), pct(sh22, 2)))
# 稳健：只依赖增速大小关系 94.9%±0.05 vs 93.3%±0.05，稳健

# C：十三五 = 2016-2020
yrs = ["2016", "2017", "2018", "2019", "2020"]
spec = {y: T[y][1] for y in yrs}
f = lambda e: sum(e.values()) / 60
c, lo, hi, _ = corners(spec, f)
print("C：十三五(2016-2020)出游合计=%s 亿人次，月均=%s 亿人次（区间[%s,%s]）≈4 → 正确" % (
    fx(sum(frac(T[y][1]) for y in yrs), 1), fx(c, 4), fx(lo, 4), fx(hi, 4)))
alt = sum(frac(T[y][1]) for y in ["2015", "2016", "2017", "2018", "2019"]) / 60
print("   若误把十三五当2015-2019：月均=%s（亦≈4，不影响）" % fx(alt, 3))

# D：2018-2022 总花费最多年份（2019）其增量是否也最多
print("D：2018-2022 年总花费与同比增量：")
incs = {}
for y in range(2018, 2023):
    incs[y] = frac(T[str(y)][2]) - frac(T[str(y - 1)][2])
    print("   %d 花费=%s 增量=%s" % (y, T[str(y)][2], fx(incs[y], 1)))
mx = max(range(2018, 2023), key=lambda y: frac(T[str(y)][2]))
mi = max(incs, key=lambda y: incs[y])
print("   花费最多年份=%d，增量最多年份=%d → D %s" % (mx, mi, "正确" if mx == mi else "错误"))
print("   舍入敏感性：2019增量0.6±0.1、2021增量0.7±0.1 区间重叠 → D 的'错'依赖显示值（按表值判断 D 错）")
print("盲解答案：C")
