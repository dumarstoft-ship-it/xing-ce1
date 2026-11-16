"""M05 第38题：苹果、梨、香蕉共420千克；苹果比梨多1/3，香蕉比苹果少1/4；
进价3、4、7元/千克，全部按6元/千克售出，求获利。
"""
from fractions import Fraction as F

# 设梨为 p 千克
# 苹果 = p*(1+1/3)，香蕉 = 苹果*(1-1/4) = p
ratio_apple = F(4, 3)
ratio_banana = ratio_apple * F(3, 4)
p = F(420) / (1 + ratio_apple + ratio_banana)
apple, pear, banana = ratio_apple * p, p, ratio_banana * p
print("苹果、梨、香蕉(千克):", apple, pear, banana)
assert (apple, pear, banana) == (168, 126, 126)

cost = 3 * apple + 4 * pear + 7 * banana
revenue = 6 * 420
profit = revenue - cost
print("成本:", cost, "收入:", revenue, "利润:", profit)
assert profit == 630

# 简便算法：梨和香蕉重量相同，两者平均进价(4+7)/2=5.5；
# 每千克利润：苹果 6-3=3，梨+香蕉 6-5.5=0.5；168*3 + 252*0.5 = 504 + 126 = 630
assert 168 * 3 + 252 * F(1, 2) == 630
print("答案: B 630")
