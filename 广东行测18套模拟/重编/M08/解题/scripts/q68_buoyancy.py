"""M08 第68题：相同实心球，甲中漂浮(部分露出)，乙中悬浮(全浸没、未触底)，液面相平，烧杯相同。
随机取参数检验四个选项的真假。"""
import random
random.seed(0)
g = 9.8
res = {'A': set(), 'B': set(), 'C': set(), 'D': set()}
for _ in range(20000):
    S = random.uniform(50e-4, 200e-4)      # 烧杯底面积 m^2
    V = random.uniform(5e-6, 50e-6)        # 球体积 m^3
    rb = random.uniform(500, 3000)         # 球密度
    r1 = rb*random.uniform(1.05, 3)        # 甲液体密度 > 球（漂浮）
    r2 = rb                                # 乙液体密度 = 球（悬浮）
    h = random.uniform(0.08, 0.2)
    if S*h < 2*V: continue
    V1 = rb*V/r1                           # 甲中排开体积
    F1, F2 = r1*g*V1, r2*g*V               # 浮力
    m1, m2 = r1*(S*h-V1), r2*(S*h-V)       # 液体质量
    p1, p2 = r1*g*h, r2*g*h                # 杯底液体压强
    res['A'].add(F2 < F1 - 1e-12)          # 乙排开液体重力更小？
    res['B'].add(p2 > p1)                  # 乙杯底压强更大？
    res['C'].add(m1 < m2)                  # 甲液体质量更小？
    res['D'].add(p1*S > p2*S)              # 甲液体对杯底压力更大？
    assert abs(F1 - rb*g*V) < 1e-9 and abs(F2 - rb*g*V) < 1e-9
print({k: sorted(v) for k, v in res.items()})
assert res == {'A': {False}, 'B': {False}, 'C': {False}, 'D': {True}}
print('只有D恒成立')
