"""M09 第68题：仓库报警电路。按题图连线：
  左竖线（电源一端）—上方导线（电铃）—右上角—R1—右侧中点；
  左竖线中点—监控机A—R2—右侧中点；右侧中点—右竖线下段—电源另一端。
  即“电铃+R1”串联支路与“监控机A+R2”串联支路并联，直接接在电源两端。
火情：温度升高，R1减小。核验各选项（先按电源电压不变；再看计内阻时的情形，作为题设隐含条件的说明）。"""

def solve(E, r, Rb, R1, RA, R2):
    R_up = Rb + R1                     # 电铃支路
    R_mid = RA + R2                    # 监控机支路
    R_par = R_up * R_mid / (R_up + R_mid)
    I = E / (R_par + r)
    U = E - I * r                      # 路端电压
    I_up, I_mid = U / R_up, U / R_mid
    return dict(U=U, I_mid=I_mid, U_bell=I_up * Rb, U_R2=I_mid * R2, I_bell=I_up)

base = dict(E=12.0, Rb=20.0, RA=30.0, R2=50.0)
for r in (0.0, 1.0):
    before = solve(r=r, R1=100.0, **base)
    after = solve(r=r, R1=10.0, **base)
    tag = '理想电源(r=0)' if r == 0 else '计内阻(r=1Ω)'
    print(tag)
    for k in ('I_mid', 'U_bell', 'U_R2', 'U'):
        print(f'   {k:7s} {before[k]:.4f} → {after[k]:.4f}', '增大' if after[k] > before[k] + 1e-12 else ('减小' if after[k] < before[k] - 1e-12 else '不变'))
ideal_b, ideal_a = solve(r=0, R1=100.0, **base), solve(r=0, R1=10.0, **base)
assert abs(ideal_a['I_mid'] - ideal_b['I_mid']) < 1e-12        # A 错：监控机电流不变
assert ideal_a['U_bell'] > ideal_b['U_bell']                    # B 错：电铃电压增大
assert abs(ideal_a['U_R2'] - ideal_b['U_R2']) < 1e-12          # C 对
assert abs(ideal_a['U'] - ideal_b['U']) < 1e-12                # D 错：电源电压不变
print('理想电源下只有C成立。')
