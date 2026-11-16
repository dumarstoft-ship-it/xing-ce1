# 第37题：甲乙合作5天完成1/3；随后甲丙合作，总用时13天（甲丙做了8天完成2/3）；乙丙6天完成60%
from fractions import Fraction as F
jy = F(1, 3) / 5          # 甲+乙
jb = F(2, 3) / (13 - 5)   # 甲+丙
yb = F(60, 100) / 6       # 乙+丙
tot = (jy + jb + yb) / 2
jia, yi, bing = tot - yb, tot - jb, tot - jy
print("甲乙", jy, "甲丙", jb, "乙丙", yb, "三队", tot, "各队", jia, yi, bing)
assert min(jia, yi, bing) > 0
print("三队合作天数", 1 / tot)          # 8
# 错误：把13天当成甲丙合作的天数 → 甲丙=2/39
tot_wrong = (jy + F(2, 3) / 13 + yb) / 2
print("误把13天当甲丙合作时间 →", 1 / tot_wrong, float(1 / tot_wrong))
