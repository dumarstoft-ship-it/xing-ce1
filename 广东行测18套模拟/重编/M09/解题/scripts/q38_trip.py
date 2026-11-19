"""M09 第38题：速度20km/h准时到，24km/h提早5分钟到，求距离。 选项 A8 B10 C12 D16
核验：D/20 − D/24 = 5/60 → D/120 = 1/12 → D=10；再逐个代入选项。"""
from fractions import Fraction as F
D = F(5, 60) / (F(1, 20) - F(1, 24))
print('方程解 D =', D)
opts = {'A': 8, 'B': 10, 'C': 12, 'D': 16}
for k, v in opts.items():
    t20, t24 = F(v, 20) * 60, F(v, 24) * 60
    print(f'{k}: {v}km  20km/h用{t20}分钟，24km/h用{t24}分钟，差{t20 - t24}分钟')
ok = [k for k, v in opts.items() if (F(v, 20) - F(v, 24)) * 60 == 5]
assert ok == ['B'] and D == 10
# 比例法：速度比5:6 → 时间比6:5，差1份=5分钟 → 原时间30分钟，距离20×0.5=10
assert 20 * F(6 * 5, 60) == 10
# 易错：5分钟不换算成小时 → D/120=5 → 600（不在选项）
print('5分钟误当5小时：', 5 / (F(1, 20) - F(1, 24)))
