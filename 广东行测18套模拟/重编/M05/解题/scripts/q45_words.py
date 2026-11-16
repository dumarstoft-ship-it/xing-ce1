"""M05 第45题：从今年3月开始背单词，每月比上月多10个，第四季度月均95个。
明年上半年总量要比今年下半年（环比的上一期）翻一番，求明年上半年月均背诵量。
"""
from fractions import Fraction as F

# 设3月背 a 个，则第 k 月（3<=k<=12）背 a+10*(k-3)
sols = []
for a in range(0, 1000):
    month = {k: a + 10 * (k - 3) for k in range(3, 13)}
    if F(month[10] + month[11] + month[12], 3) == 95:
        sols.append((a, month))
assert len(sols) == 1
a, month = sols[0]
print("3月背", a, "个；各月:", month)
h2 = sum(month[k] for k in range(7, 13))
print("今年下半年(7-12月)总量:", h2)
target_total = 2 * h2
avg = F(target_total, 6)
print("明年上半年目标总量:", target_total, "月均:", avg)
assert (h2, target_total, avg) == (480, 960, 160)

# 对照：若误用今年上半年(仅3-6月有量)作比较基数
h1 = sum(month[k] for k in range(3, 7))
print("对照：今年上半年总量", h1, "，翻一番后月均", F(2 * h1, 6), "（属同比口径，不是环比）")
print("答案: D 160")
