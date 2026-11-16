"""第45题：按60%利润率定价，每场卖100公斤；打九折后每公斤利润少9.6元，销量升10%。
打折后每场总利润与原来相比如何？
选项 A降低15%以上 B降低不到15% C提高15%以上 D提高不到15%

核验：利润率按行测通行口径（利润/成本）。设成本 c，定价 1.6c，九折少收 0.16c=9.6 => c=60。
另附"利润/售价"口径的对照（非通行口径），只用于说明 9.6 元并不影响比较结果的方向判断。
"""
from fractions import Fraction as F

c = F(96, 10) / F(16, 100)       # 0.16c = 9.6
price = F(16, 10) * c
new_price = price * F(9, 10)
p_old = price - c
p_new = new_price - c
tot_old = p_old * 100
tot_new = p_new * 110
chg = (tot_new - tot_old) / tot_old
print("成本", c, "原价", price, "折后价", new_price)
print("原单件利润", p_old, "折后单件利润", p_new, "（减少%s）" % (p_old - p_new))
print("原总利润", tot_old, "折后总利润", tot_new, "变化率 %.2f%%" % (float(chg) * 100))
print("不依赖 9.6 的比值：0.44c×110 / (0.6c×100) =", F(44, 100) * 110 / (F(6, 10) * 100))

if chg < 0:
    print("对应选项", "A 降低15%以上" if -chg > F(15, 100) else "B 降低不到15%")
else:
    print("对应选项", "C 提高15%以上" if chg > F(15, 100) else "D 提高不到15%")

# 对照：若把利润率理解为 利润/售价
price2 = F(96, 10) / F(1, 10)
cost2 = price2 * F(4, 10)
chg2 = ((price2 * F(9, 10) - cost2) * 110 - (price2 - cost2) * 100) / ((price2 - cost2) * 100)
print("[对照] 利润/售价口径下的变化率 %.2f%%（非行测通行口径）" % (float(chg2) * 100))
