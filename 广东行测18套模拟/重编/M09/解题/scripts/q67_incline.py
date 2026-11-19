"""M09 第67题：M在沿斜面向上的恒力F作用下沿粗糙斜面匀速上滑，找不准确的说法。
核验：取 m=1kg、g=10、θ=20°、μ=0.3，按受力平衡算出F，检验各说法。"""
from math import sin, cos, radians, isclose
m, g, th, mu = 1.0, 10.0, radians(20), 0.3
N = m * g * cos(th)                 # 支持力，垂直斜面
f = mu * N                          # 滑动摩擦力，沿斜面向下（与运动方向相反）
F = m * g * sin(th) + f             # 匀速：沿斜面方向合力为0
print(f'G={m*g:.2f}N(竖直向下)  N={N:.2f}N(垂直斜面)  f={f:.2f}N(沿斜面向下)  F={F:.2f}N(沿斜面向上)')
s = 1.0
print(f'F做功 {F*s:.2f}J>0（A准确）；上升高度 {s*sin(th):.3f}m，重力势能增大（B准确）；摩擦力与运动方向相反（C准确）')
print('支持力与重力：大小', round(N, 2), 'vs', m * g, '，方向也不在同一直线上 → 不是平衡力（D不准确）')
assert not isclose(N, m * g)
# 真正平衡的是四个力的合力：F + N + f + G = 0
fx = F - f - m * g * sin(th); fy = N - m * g * cos(th)
assert isclose(fx, 0, abs_tol=1e-12) and isclose(fy, 0, abs_tol=1e-12)
