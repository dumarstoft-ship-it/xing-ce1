"""M11 第67题：A在水平推力F作用下静止在B的光滑斜面上，B静止在水平地面上。取数检验。
选项 A B共受3个力  B B受摩擦力大小等于F  C A对B的作用力大小为F  D A、B相互作用力大小不等
题图：A、B拼成矩形，对角线从左上到右下，A在右上、B在左下；F水平向左作用在A上，把A压向斜面。"""
from math import radians, tan, cos, sin, hypot, isclose
g, mA, mB = 10.0, 2.0, 5.0
theta = radians(40)                       # 斜面倾角（取值不影响结论）
GA = mA * g
F = GA * tan(theta)                       # 光滑斜面上A平衡所需的水平推力
N = GA / cos(theta)                       # 斜面对A的支持力（垂直斜面）
assert isclose(N * sin(theta), F) and isclose(N * cos(theta), GA)
# B受力：重力、地面支持力、A对B的压力N（垂直斜面向左下）、地面静摩擦力（水平向右）
N_ground = mB * g + N * cos(theta)
f_ground = N * sin(theta)
forces_on_B = {'重力': mB * g, '地面支持力': N_ground, 'A的压力': N, '地面摩擦力': f_ground}
print('B受力：', {k: round(v, 2) for k, v in forces_on_B.items()}, '共', len(forces_on_B), '个')
print('F =', round(F, 2), '；地面对B的摩擦力 =', round(f_ground, 2), '；A对B的作用力 =', round(N, 2), '=√(F²+G_A²) =', round(hypot(F, GA), 2))
truth = {'A': len(forces_on_B) == 3, 'B': isclose(f_ground, F), 'C': isclose(N, F), 'D': False}  # D违反牛顿第三定律
print(truth)
assert [k for k, v in truth.items() if v] == ['B']
