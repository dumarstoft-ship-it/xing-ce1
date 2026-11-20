"""S02 第37题：乙做200个时甲完成总量一半；完工时甲完成总量3/5；效率不变，求总量。 选项 A500 B600 C640 D800"""
from fractions import Fraction as F
ratio = F(3, 5) / F(2, 5)            # 甲∶乙 = 3∶2
yi_share_at_half = F(1, 2) / ratio   # 甲完成1/2时，乙完成1/3
total = 200 / yi_share_at_half
print('甲乙效率比', ratio, '；甲完成一半时乙完成', yi_share_at_half, '；总量', total)
assert total == 600
