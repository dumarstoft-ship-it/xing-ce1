#!/usr/bin/env python3
"""M04 资料分析第4组（第86—90题）：2023年8月全国及部分城市汽车上牌量。

用法：python3 q86-90_m4_car.py
文字与表格从 ../../输入/data.json 读取，先核对要用的数字确在原文中，再逐题精确计算。
"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / '输入' / 'data.json'
MID = 'gd-mock-2026h2-s19-m4'

d = json.loads(DATA.read_text(encoding='utf-8'))
m = next(m for m in d['materials'] if m['id'] == MID)
text = m['blocks'][0]['text']
tb = m['blocks'][1]
for s in ['全国汽车总上牌量167.3万辆，环比增长9.1%', 'SUV上牌量77.0万辆，占全国汽车总上牌量的46.0%，环比提高1.6个百分点',
          '轿车上牌量82.8万辆，占比49.5%']:
    assert s in text, s


def num(s):
    return None if s == '—' else float(s.replace('−', '-'))


C = {}
for r in tb['rows']:
    C[r[0]] = dict(n=int(r[1]), g=num(r[2]), prov=num(r[3]), top=r[4], topn=int(r[5]))
NAT, GN = 167.3, 9.1
SUV, SUVS, SUVD = 77.0, 46.0, 1.6
CAR, CARS = 82.8, 49.5


def pick(value, opts):
    diffs = {k: abs(value - v) for k, v in opts.items()}
    return min(diffs, key=diffs.get), diffs


print('=' * 70)
print('数据自洽检查')
print(f'  SUV 77.0/167.3 = {SUV/NAT*100:.3f}%（文字46.0%）；轿车 82.8/167.3 = {CAR/NAT*100:.3f}%（文字49.5%）')
print(f'  SUV+轿车 = {SUV+CAR:.1f} ≤ 167.3，其余车型 {NAT-SUV-CAR:.1f} 万辆（{(NAT-SUV-CAR)/NAT*100:.1f}%）')
prov_sum = 0
for k, v in C.items():
    sh = v['topn'] / v['n'] * 100
    rest = v['n'] - v['topn']
    pv =v['n'] / (v['prov'] / 100) if v['prov'] else v['n']
    prov_sum += pv
    print(f'  {k}: 上牌{v["n"]}，{v["top"]} {v["topn"]}（占{sh:.1f}%，其余{rest}），'
          f'所在省份 {pv:.0f}' + ('' if v['prov'] else '（直辖市，取本身）'))
    assert v['topn'] <= v['n']
print(f'  10个城市所在省级单位合计 {prov_sum:.0f} 辆 = {prov_sum/1e4:.2f} 万辆 < 全国167.3万辆 → 无矛盾')
print('  表格标题未标“图”，按表格排印。')

print('=' * 70)
print('第86题  SUV环比增速（由比重变化反推）')
nat7 = NAT / (1 + GN / 100)
s7 = SUVS - SUVD
suv7 = nat7 * s7 / 100
v86 = (SUV / suv7 - 1) * 100
v86b = ((1 + GN / 100) * SUVS / s7 - 1) * 100
v86c = (SUV / (nat7 * (SUV / NAT * 100 - SUVD) / 100) - 1) * 100
print(f'  7月总量 = 167.3/1.091 = {nat7:.4f}；7月SUV比重 = 46.0−1.6 = {s7:.1f}%；7月SUV = {suv7:.4f} 万辆')
print(f'  增速 = 77.0/{suv7:.4f} − 1 = {v86:.4f}%')
print(f'  公式法 (1+9.1%)×46.0/44.4 − 1 = {v86b:.4f}%；用精确比重 {SUV/NAT*100:.4f}% 算得 {v86c:.4f}%')
a86, dd = pick(v86, {'A': 13.1, 'B': 12.0, 'C': 10.5, 'D': 9.1})
assert all(pick(v, {'A': 13.1, 'B': 12.0, 'C': 10.5, 'D': 9.1})[0] == a86 for v in (v86b, v86c))
print(f'  → {a86}  偏差 {dd}')

print('=' * 70)
print('第87题  7月 > (7月+8月)/2 ⇔ 7月 > 8月 ⇔ 8月环比增速 < 0')
c87 = []
for k, v in C.items():
    jul = v['n'] / (1 + v['g'] / 100)
    avg = (jul + v['n']) / 2
    if jul > avg:
        c87.append(k)
    print(f'  {k}: 7月 {jul:.1f}，7—8月月均 {avg:.1f}，环比 {v["g"]:+.1f}%' + ('  ← 7月高于月均' if jul > avg else ''))
a87, _ = pick(len(c87), {'A': 8, 'B': 4, 'C': 2, 'D': 1})
print(f'  个数 {len(c87)}（{c87}）→ {a87}')

print('=' * 70)
print('第88题  广东 = 广州÷25.4%，湖北 = 武汉÷62.1%')
gd = C['广州']['n'] / (C['广州']['prov'] / 100)
hb = C['武汉']['n'] / (C['武汉']['prov'] / 100)
v88 = gd / hb
print(f'  广东 {gd:.2f}，湖北 {hb:.2f}，倍数 {v88:.4f}')
a88, dd = pick(v88, {'A': 1.4, 'B': 2.4, 'C': 3.4, 'D': 4.4})
print(f'  → {a88}  偏差 {dd}')
print(f'  干扰：A≈广州/武汉 = {C["广州"]["n"]/C["武汉"]["n"]:.4f}')

print('=' * 70)
print('第89题  郑州、杭州、苏州轿车之和 ÷ 三城总上牌量')
three = ['郑州', '杭州', '苏州']
assert all(C[k]['top'] == '轿车' for k in three)
car3 = sum(C[k]['topn'] for k in three)
tot3 = sum(C[k]['n'] for k in three)
v89 = car3 / tot3 * 100
print(f'  {car3}/{tot3} = {v89:.4f}%')
a89, dd = pick(v89, {'A': 47.3, 'B': 50.4, 'C': 52.5, 'D': 55.7})
print(f'  → {a89}  偏差 {dd}')

print('=' * 70)
print('第90题')
sc = C['成都']['n'] / (C['成都']['prov'] / 100)
cd_non_suv = C['成都']['n'] - C['成都']['topn']
print(f'  A：四川总上牌量 = 53142÷67% = {sc:.1f} 辆（约8万是全部车型）；'
      f'成都非SUV {cd_non_suv} 辆 ⇒ 四川SUV ≤ {sc - cd_non_suv:.0f} 辆，不可能约8万 → 错')
down = [k for k, v in C.items() if v['g'] < GN]
print(f'  B：比重下降 ⇔ 城市环比增速 < 全国9.1%：{down}，共 {len(down)} 个，不是7个 → 错')
cd7 = C['成都']['n'] / (1 + C['成都']['g'] / 100)
gz7 = C['广州']['n'] / (1 + C['广州']['g'] / 100)
print(f'  C：7月成都 {cd7:.1f} > 广州 {gz7:.1f} → 错')
sz_suv_max = C['苏州']['n'] - C['苏州']['topn']
cq_suv = C['重庆']['topn']
assert C['苏州']['top'] == '轿车' and C['重庆']['top'] == 'SUV'
print(f'  D：苏州轿车最多 {C["苏州"]["topn"]}，SUV ≤ 36890−19774 = {sz_suv_max} < 重庆SUV {cq_suv} → 对'
      f'（仅用“SUV不多于轿车”只能得 ≤19774，不足以判断，须用 SUV+轿车 ≤ 总量）')
assert sz_suv_max < cq_suv and len(down) != 7 and cd7 > gz7 and sc - cd_non_suv < 60000
print('  → D')

print('=' * 70)
print(f'答案：86{a86} 87{a87} 88{a88} 89{a89} 90D')
