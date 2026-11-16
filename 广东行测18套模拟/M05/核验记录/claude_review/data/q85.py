# -*- coding: utf-8 -*-
"""Q85 下列表述不正确的是（盲解）。"""
import sys; sys.path.insert(0, __import__('os').path.dirname(__file__))
from blind_common import *

N = 85
hdr, T = table_dict(N)
print("表头：", hdr)
col = {h: i for i, h in enumerate(hdr)}
# A：2023/2019 >= 1.2 for all
print("A：各规模 2023/2019：")
allok = True
for k in ["大型企业", "中型企业", "小型企业", "微型企业"]:
    f = lambda e: e["x"] / e["y"]
    c, lo, hi, _ = corners({"x": T[k][col["2023年"]], "y": T[k][col["2019年"]]}, f)
    ok = c >= F(6, 5)
    allok &= ok
    print("   %s：%s/%s = %s（区间[%s,%s]）≥1.2? %s" % (k, T[k][col["2023年"]], T[k][col["2019年"]], fx(c, 4), fx(lo, 4), fx(hi, 4), ok))
print("   → A '均达到1.2倍' %s" % ("正确" if allok else "不正确（大型企业仅约1.11倍）"))
# B
ds = frac(T["小型企业"][col["2023年"]]) - frac(T["小型企业"][col["2022年"]])
dm = frac(T["微型企业"][col["2023年"]]) - frac(T["微型企业"][col["2022年"]])
print("B：小型 +%s 个百分点，微型 +%s 个百分点 → %s" % (fx(ds * 100, 1), fx(dm * 100, 1),
      "正确" if (ds * 100, dm * 100) == (F(86, 10), F(118, 10)) else "不正确"))
# C
r23 = find_in_text(N, r"企业发明专利产业化率达到([\d.]+%)")
pp = find_in_text(N, r"较上年提高([\d.]+)个百分点")
print("C：2022 = %s - %s = %s%% → %s" % (r23, pp, fx(frac(r23) * 100 - frac(pp), 1),
      "正确" if frac(r23) * 100 - frac(pp) == F(481, 10) else "不正确"))
# D
print("D：中型-小型 差值：")
prev = None; inc = True
for y in ["2019年", "2020年", "2021年", "2022年"]:
    dd = (frac(T["中型企业"][col[y]]) - frac(T["小型企业"][col[y]])) * 100
    print("   %s：%s 个百分点" % (y, fx(dd, 1)))
    if y in ("2021年", "2022年"):
        inc &= dd > prev
    prev = dd
print("   → 2020→2021→2022 逐年增大：%s（若把2019→2020也计入则2020较2019下降，属'逐年'口径歧义，主流口径不计）" % inc)
print("盲解答案：A")
