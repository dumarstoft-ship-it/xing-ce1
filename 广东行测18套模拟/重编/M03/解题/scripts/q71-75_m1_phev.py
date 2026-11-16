#!/usr/bin/env python3
"""M03 资料分析第1组（第71—75题）：2024年9月我国插电混动新能源汽车活跃量。

用法：python3 q71-75_m1_phev.py
三张表直接从 ../../输入/data.json 读取，逐题按材料数据精确计算，并做本组数据自洽检查。
"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / '输入' / 'data.json'
MID = 'gd-mock-2026h2-s18-m1'


def num(s):
    s = s.replace('−', '-').replace('%', '').strip()
    return float(s)


def load():
    d = json.loads(DATA.read_text(encoding='utf-8'))
    m = next(m for m in d['materials'] if m['id'] == MID)
    t1, t2, t3 = m['blocks']
    LEVEL = {r[0]: (num(r[1]), num(r[2]) / 100) for r in t1['rows']}          # 级别: (活跃量, 环比)
    SHARE = {(r[0], r[1]): num(r[2]) / 100 for r in t2['rows']}               # (级别, 厂商): 占比
    TOP = {r[0]: (num(r[1]), num(r[2]) / 100) for r in t3['rows']}            # 车系: (活跃量, 环比)
    return LEVEL, SHARE, TOP, t3['rows']


LEVEL, SHARE, TOP, TOP_ROWS = load()


def base(v, r):
    return v / (1 + r)


def pick(value, opts):
    diffs = {k: abs(value - v) for k, v in opts.items()}
    return min(diffs, key=diffs.get), diffs


print('=' * 70)
print('数据自洽检查')
for lv in LEVEL:
    s = sum(v for (l, _), v in SHARE.items() if l == lv)
    print(f'  图2 {lv} 各厂商占比之和 = {s*100:.1f}%')
tot = sum(v for v, _ in LEVEL.values())
tot0 = sum(base(v, r) for v, r in LEVEL.values())
print(f'  三个级别合计：9月 {tot:.2f} 万辆，8月 {tot0:.2f} 万辆，合计环比 {(tot/tot0-1)*100:.2f}%')
vals = [num(r[1]) for r in TOP_ROWS]
print(f'  图3 是否按活跃量降序：{vals == sorted(vals, reverse=True)}')
# 图3 与 图1×图2 的交叉核对
tengshi = LEVEL['MPV'][0] * SHARE[('MPV', '腾势汽车')]
print(f'  腾势汽车MPV = 32.81×50.9% = {tengshi:.3f} 万辆；图3 腾势D9-DM = {TOP["腾势D9-DM"][0]:.2f}（一致）')
bmw = LEVEL['轿车'][0] * SHARE[('轿车', '华晨宝马')]
print(f'  华晨宝马轿车 = {bmw:.3f} 万辆 ≥ 宝马5系PHEV {TOP["宝马5系PHEV"][0]:.2f}（不矛盾）')
byd_suv = LEVEL['SUV'][0] * SHARE[('SUV', '比亚迪')]
byd_car = LEVEL['轿车'][0] * SHARE[('轿车', '比亚迪')]
suv_models = ['比亚迪宋PLUS-DM', '比亚迪宋Pro-DM', '比亚迪唐DM']
car_models = ['比亚迪秦PLUS-DM', '比亚迪汉DM', '比亚迪驱逐舰05', '比亚迪秦L-DM', '比亚迪海豹06']
print(f'  比亚迪SUV {byd_suv:.2f} ≥ 图3中比亚迪SUV车系之和 {sum(TOP[k][0] for k in suv_models):.2f}')
print(f'  比亚迪轿车 {byd_car:.2f} ≥ 图3中比亚迪轿车车系之和 {sum(TOP[k][0] for k in car_models):.2f}')
inc_car = LEVEL['轿车'][0] - base(*LEVEL['轿车'])
inc_car_models = sum(TOP[k][0] - base(*TOP[k]) for k in car_models + ['宝马5系PHEV'])
print(f'  轿车环比增量 {inc_car:.2f} ≥ 图3轿车车系增量之和 {inc_car_models:.2f}（不矛盾）')

print('=' * 70)
print('第71题  2024年9月 比亚迪SUV − 比亚迪轿车')
v71 = byd_suv - byd_car
print(f'  {LEVEL["SUV"][0]}×58.8% − {LEVEL["轿车"][0]}×68.7% = {byd_suv:.4f} − {byd_car:.4f} = {v71:.4f} 万辆')
a71, d = pick(v71, {'A': 16.62, 'B': 22.95, 'C': 11.88, 'D': 9.25})
print(f'  → {a71}  偏差 {d}')

print('=' * 70)
print('第72题  2024年8月 SUV − MPV（基期差）')
suv0 = base(*LEVEL['SUV'])
mpv0 = base(*LEVEL['MPV'])
v72 = suv0 - mpv0
print(f'  307.08/1.056 − 32.81/1.064 = {suv0:.4f} − {mpv0:.4f} = {v72:.4f} 万辆')
print(f'  （陷阱：现期差 307.08−32.81 = {LEVEL["SUV"][0]-LEVEL["MPV"][0]:.2f}）')
a72, d = pick(v72, {'A': 241.62, 'B': 259.96, 'C': 274.27, 'D': 282.38})
print(f'  → {a72}  偏差 {d}')

print('=' * 70)
print('第73题  2024年9月 环比增量最大（现期×r/(1+r)）')
opts73 = {'A': '比亚迪驱逐舰05', 'B': '比亚迪汉DM', 'C': '比亚迪唐DM', 'D': '比亚迪宋Pro-DM'}
inc73 = {}
for k, name in opts73.items():
    v, r = TOP[name]
    inc73[k] = v - base(v, r)
    print(f'  {k} {name}: {v}×{r*100:.1f}%/(1+{r*100:.1f}%) = {inc73[k]:.4f} 万辆')
a73 = max(inc73, key=inc73.get)
print(f'  → {a73}；顺序 {sorted(inc73, key=inc73.get, reverse=True)}')
allinc = {n: TOP[n][0] - base(*TOP[n]) for n in TOP}
print('  （参考：TOP10全部车系增量）', {n: round(x, 3) for n, x in sorted(allinc.items(), key=lambda x: -x[1])})

print('=' * 70)
print('第74题  2024年8月 秦PLUS-DM 占 轿车 的比重（基期比重）')
q0 = base(*TOP['比亚迪秦PLUS-DM'])
car0 = base(*LEVEL['轿车'])
v74 = q0 / car0 * 100
cur74 = TOP['比亚迪秦PLUS-DM'][0] / LEVEL['轿车'][0] * 100
print(f'  (72.98/1.032)/(245.54/1.069) = {q0:.4f}/{car0:.4f} = {v74:.3f}%')
print(f'  公式：现期比重 {cur74:.3f}% × 1.069/1.032 = {cur74*1.069/1.032:.3f}%')
a74, d = pick(v74, {'A': 27.6, 'B': 28.2, 'C': 29.7, 'D': 30.8})
print(f'  → {a74}  偏差 {d}（C项29.7%为现期比重）')

print('=' * 70)
print('第75题  逐项判断')
lt = LEVEL['MPV'][0] * SHARE[('MPV', '岚图汽车')]
bk = LEVEL['MPV'][0] * SHARE[('MPV', '上汽通用别克')]
print(f'  A 岚图 {lt:.4f} − 别克 {bk:.4f} = {lt-bk:.4f} 万辆 = {(lt-bk)*1e4:.0f} 辆；选项说3281辆 → 错（差10倍）')
ratioB = SHARE[('轿车', '上汽集团')] / SHARE[('轿车', '上汽通用五菱')]
print(f'  B 上汽集团/上汽通用五菱 = 4.6%/2.3% = {ratioB:.4f} → 对')
print(f'    （占比为一位小数的四舍五入值，比值实际区间 {4.55/2.35:.3f}—{4.65/2.25:.3f}）')
print('  C 资料只给2024年9月活跃量和环比增长率，没有同比数据，2023年9月无法推出 → 错')
ql0 = base(*TOP['比亚迪秦L-DM'])
print(f'  D 秦L-DM 8月 = 12.62/1.459 = {ql0:.4f} 万辆 > 8 → 错')
print('  → B')

print('=' * 70)
ans = {71: a71, 72: a72, 73: a73, 74: a74, 75: 'B'}
print('本组答案：', ans)
