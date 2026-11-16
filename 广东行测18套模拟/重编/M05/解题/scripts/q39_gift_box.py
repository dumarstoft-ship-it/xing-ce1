"""M05 第39题：A按30%利润率定价，B按50%；礼盒=4A+2B，按定价总和八八折出售，每盒获利80元；
A的成本比B低30元，求B的定价。先精确解方程，再枚举整数成本确认唯一。
"""
from fractions import Fraction as F


def box_profit(b_cost):
    a_cost = b_cost - 30
    a_price = a_cost * F(13, 10)
    b_price = b_cost * F(3, 2)
    sale = (4 * a_price + 2 * b_price) * F(88, 100)
    cost = 4 * a_cost + 2 * b_cost
    return sale - cost


# 利润是 b_cost 的一次函数：profit = k*b + m
m = box_profit(F(0))
k = box_profit(F(1)) - m
b_cost = (80 - m) / k
print("profit = ", k, "* b +", m, "=> B成本 b =", b_cost)
assert b_cost == 80

sols = [b for b in range(31, 5001) if box_profit(F(b)) == 80]
print("枚举整数成本得到的解:", sols)
assert sols == [80]

a_cost = b_cost - 30
a_price, b_price = a_cost * F(13, 10), b_cost * F(3, 2)
total_price = 4 * a_price + 2 * b_price
print("A成本", a_cost, "定价", a_price, "；B成本", b_cost, "定价", b_price)
print("礼盒定价总和", total_price, "，八八折售价", total_price * F(88, 100), "，礼盒成本", 4 * a_cost + 2 * b_cost)
assert b_price == 120
print("答案: A 120（D项80是B的成本）")
