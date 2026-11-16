# 第78题：四项 2023 年同比增速排序，并检验舍入（人次±0.05亿、增速±0.05个百分点）是否改变排序
import itertools, random

T, gT = 48.9, 0.933      # ① 全国国内出游人次（亿人次）、增速
U, gU = 37.6, 0.949      # ② 城镇居民国内出游人次、增速
gRS = 1.064              # ④ 农村居民国内出游花费增速 106.4%

def rural_growth(T, gT, U, gU, base_total=None):
    R = T - U
    T0 = base_total if base_total is not None else T / (1 + gT)
    U0 = U / (1 + gU)
    return R / (T0 - U0) - 1, R, T0 - U0

g3, R, R0 = rural_growth(T, gT, U, gU)
print(f'③ 农村居民人次：2023年 {R:.1f} 亿，2022年 ≈ {T/(1+gT):.3f}−{U/(1+gU):.3f} = {R0:.3f} 亿，增速 ≈ {g3*100:.1f}%')
g3b, _, R0b = rural_growth(T, gT, U, gU, base_total=25.3)
print(f'   用表中2022年总量25.3亿作基期：农村2022 ≈ {R0b:.3f} 亿，增速 ≈ {g3b*100:.1f}%')
print(f'① {gT*100:.1f}%  ② {gU*100:.1f}%  ③ {g3*100:.1f}%  ④ {gRS*100:.1f}%')
vals = {'①': gT, '②': gU, '③': g3, '④': gRS}
print('从高到低：', ''.join(sorted(vals, key=lambda k: -vals[k])))

# 舍入区间：人次±0.05亿，增速±0.05个百分点；取所有端点组合 + 随机抽样
rng = {'T': (48.85, 48.95), 'gT': (0.9325, 0.9335), 'U': (37.55, 37.65), 'gU': (0.9485, 0.9495), 'g4': (1.0635, 1.0645)}
orders = set(); lo, hi = 9, -9
def check(t, gt, u, gu, g4):
    global lo, hi
    g3, _, _ = rural_growth(t, gt, u, gu)
    lo, hi = min(lo, g3), max(hi, g3)
    v = {'①': gt, '②': gu, '③': g3, '④': g4}
    orders.add(''.join(sorted(v, key=lambda k: -v[k])))
for combo in itertools.product(*rng.values()):
    check(*combo)
random.seed(0)
for _ in range(200000):
    check(*[random.uniform(a, b) for a, b in rng.values()])
print(f'舍入范围内 ③ 增速区间：{lo*100:.1f}% ～ {hi*100:.1f}%')
print('舍入范围内出现过的排序：', orders)
