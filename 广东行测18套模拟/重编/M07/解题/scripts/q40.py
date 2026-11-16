# 第40题：甲单独20天。甲做5天后乙加入，计划提前5天（共15天）完工。
# 实际完成2/5时乙退出丙加入，最终只提前3天（共17天）。求乙:丙效率
from fractions import Fraction as F
T = 20                     # 总量取20，甲效率1
jia = F(1)
# 计划：前5天甲做5，后10天甲乙合做15
yi = F(T - 5, 15 - 5) - jia
# 实际：2/5 = 8；甲先做5，甲乙再做3用 3/(1+yi) 天
t1 = 5 + (F(2, 5) * T - 5) / (jia + yi)
rest_days = 17 - t1
bing = (T - F(2, 5) * T) / rest_days - jia
print("乙效率", yi, "完成2/5的时刻", t1, "甲丙合作天数", rest_days, "丙效率", bing, "乙:丙", yi / bing)
assert yi / bing == F(5, 2)
# 检查“2/5时乙已加入”：甲独做5天只完成1/4<2/5，成立
assert F(5, T) < F(2, 5)
# 错误思路：以为完成2/5时乙尚未加入或忽略甲先做的5天：甲乙从0做到2/5 → 用时8/1.5=16/3天，
# 剩12份在 17-5-16/3 天内由甲丙完成
t_wrong = 5 + F(8) / (jia + yi)
b_wrong = 12 / (17 - t_wrong) - 1
print("错误思路（2/5从乙加入算起）丙效率", b_wrong, "乙:丙", yi / b_wrong if b_wrong else None)
