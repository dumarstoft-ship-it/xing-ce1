"""M10 第69题：海水密度受温度、盐度影响，判断哪种海水密度大。用UNESCO EOS-80一个大气压下的状态方程计算。
选项 A越热越咸 B越冷越咸 C越冷越淡 D越热越淡"""
def rho(S, T):
    rw = (999.842594 + 6.793952e-2 * T - 9.095290e-3 * T ** 2 + 1.001685e-4 * T ** 3
          - 1.120083e-6 * T ** 4 + 6.536332e-9 * T ** 5)
    A = 8.24493e-1 - 4.0899e-3 * T + 7.6438e-5 * T ** 2 - 8.2467e-7 * T ** 3 + 5.3875e-9 * T ** 4
    B = -5.72466e-3 + 1.0227e-4 * T - 1.6546e-6 * T ** 2
    C = 4.8314e-4
    return rw + A * S + B * S ** 1.5 + C * S ** 2
assert abs(rho(35, 25) - 1023.343) < 0.01      # 手册校验值 (S=35, T=25℃)
combos = {'A 热+咸': (37, 28), 'B 冷+咸': (37, 2), 'C 冷+淡': (33, 2), 'D 热+淡': (33, 28)}
for k, (S, T) in combos.items():
    print(k, 'S=%d T=%d℃ ρ=%.2f kg/m³' % (S, T, rho(S, T)))
best = max(combos, key=lambda k: rho(*combos[k]))
print('密度最大：', best)
# 海洋常见范围内单调性：温度越低、盐度越高，密度越大
assert all(rho(S, T) > rho(S, T + 1) for S in range(30, 41) for T in range(0, 30))
assert all(rho(S + 1, T) > rho(S, T) for S in range(30, 40) for T in range(0, 31))
assert best.startswith('B')
