"""S01 第37题：甲15天、乙30天，合作完成，按工作量分配，甲得15000元，乙得多少。 选项 A5000 B7500 C15000 D30000"""
from fractions import Fraction as F
ea, eb = F(1, 15), F(1, 30)
t = 1 / (ea + eb)                       # 合作10天
wa, wb = ea * t, eb * t
pay_b = 15000 * wb / wa
print('合作', t, '天，甲完成', wa, '乙完成', wb, '乙应得', pay_b)
assert pay_b == 7500
# 易错核对：按单独完成所需时间之比（乙30天是甲15天的2倍）分配 → 30000（D）
print('按时间比分配乙得', 15000 * 30 // 15)
