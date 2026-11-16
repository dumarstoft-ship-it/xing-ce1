"""M08 第45题：瓶身圆柱、底面积S。正放水高12cm=瓶高一半→瓶高24cm；倒置后水面上升1/3→水高16cm，
上方空气为圆柱段 24-16=8cm。水体积=12S，瓶容积=12S+8S。"""
from fractions import Fraction as F
H = 24; h1 = 12; h2 = h1*F(4, 3)
water = h1; air = H - h2
ratio = F(water, water + air)
print('倒置后水高', h2, '空气柱高', air, '水/瓶 =', ratio)
assert ratio == F(3, 5)
# 图上量尺：原图像素，底部 y≈190，12cm 线 y≈101，上虚线 y≈71
px_per_cm = (190-101)/12
print('图中上虚线高度约', (190-71)/px_per_cm, 'cm（与16cm吻合）')
print('误按 水高/瓶高 = 12/24 =', F(12, 24), '；误按倒置后 16/24 =', F(16, 24))
