#!/usr/bin/env python3
"""M03 资料分析第4组（第86—90题）：2024年我国节假日及春运期间出行情况。

用法：python3 q86-90_m4_holiday.py
表格从 ../../输入/data.json 读取，逐题精确计算，并做本组数据自洽检查
（总量÷天数 与 四种方式日均量之和；分项基期之和推出的合计增速 与 表中合计增速）。
"""
import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / '输入' / 'data.json'
MID = 'gd-mock-2026h2-s18-m4'

d = json.loads(DATA.read_text(encoding='utf-8'))
m = next(m for m in d['materials'] if m['id'] == MID)
tb = m['blocks'][0]
MODES = ['铁路', '公路', '民航', '水路']


def num(s):
    s = s.replace('−', '-').replace('%', '').strip()
    return None if s in ('—', '') else float(s)


V, G, DAYS, ORDER = {}, {}, {}, []
for row in tb['rows']:
    period, item, *vals = row
    key = period.split('（')[0]
    DAYS[key] = int(re.search(r'（(\d+)天）', period).group(1))
    vals = [num(x) for x in vals]
    if item == '数值':
        V[key] = dict(zip(['总量'] + MODES, vals))
        ORDER.append(key)
    else:
        G[key] = dict(zip(['总量'] + MODES, [None if x is None else x / 100 for x in vals]))


def base(p, k):
    return V[p][k] / (1 + G[p][k])


def pick(value, opts):
    diffs = {k: abs(value - v) for k, v in opts.items()}
    return min(diffs, key=diffs.get), diffs


print('=' * 70)
print('数据自洽检查')
for p in ORDER:
    daily_tot = V[p]['总量'] / DAYS[p]
    s = sum(V[p][k] for k in MODES)
    line = f'  {p}（{DAYS[p]}天）：总量/天数 {daily_tot:.2f}，四项日均和 {s:.2f}，差 {daily_tot-s:+.2f}'
    if all(G[p][k] is not None for k in MODES):
        b = sum(base(p, k) for k in MODES)
        g = (s / b - 1) * 100
        # 各分项增速按±0.05个百分点的舍入区间，求合计增速可能范围
        lo = (s / sum(V[p][k] / (1 + G[p][k] - 0.0005) for k in MODES) - 1) * 100
        hi = (s / sum(V[p][k] / (1 + G[p][k] + 0.0005) for k in MODES) - 1) * 100
        flag = '一致' if lo - 0.05 <= G[p]['总量'] * 100 <= hi + 0.05 else '不一致'
        line += f'；分项推出合计增速 {g:.2f}%（舍入区间 {lo:.2f}—{hi:.2f}%），表中 {G[p]["总量"]*100:.1f}% → {flag}'
    print(line)

print('=' * 70)
print('第86题  七个时期全社会跨区域客流总量之和')
s86 = sum(V[p]['总量'] for p in ORDER)
print(f'  合计 {s86:.1f} 万人次 = {s86/1e4:.4f} 亿人次')
a86, dd = pick(s86 / 1e4, {'A': 137, 'B': 139, 'C': 141, 'D': 143})
print(f'  → {a86}  偏差 {dd}')

print('=' * 70)
print('第87题  2023年 端午、五一、春运、元旦 铁路日均客流量 由低到高')
b87 = {p: base(p, '铁路') for p in ['端午假期', '五一假期', '春运期间', '元旦假期']}
for p, v in b87.items():
    print(f'  {p}: {V[p]["铁路"]}/(1+{G[p]["铁路"]*100:.1f}%) = {v:.3f}')
order87 = [p.replace('期间', '').replace('假期', '') for p in sorted(b87, key=b87.get)]
print('  由低到高：', order87)
opts87 = {'A': ['元旦', '春运', '端午', '五一'], 'B': ['春运', '元旦', '端午', '五一'],
          'C': ['五一', '端午', '春运', '元旦'], 'D': ['元旦', '端午', '春运', '五一']}
a87 = next(k for k, v in opts87.items() if v == order87)
print(f'  → {a87}')
print('  （参考：2024年现期由低到高：', [p for p in sorted(b87, key=lambda p: V[p]['铁路'])], '）')

print('=' * 70)
print('第88题  2024年 民航日均 超过 水路日均 2倍 的时期数')
ratio = {p: V[p]['民航'] / V[p]['水路'] for p in ORDER}
for p, r in ratio.items():
    print(f'  {p}: {V[p]["民航"]}/{V[p]["水路"]} = {r:.4f}  {"＞2" if r > 2 else ""}')
n2 = sum(r > 2 for r in ratio.values())
n3 = sum(r > 3 for r in ratio.values())
print(f'  比值＞2：{n2} 个；（若按“多2倍”即比值＞3理解：{n3} 个，不在选项中）')
a88 = {1: 'A', 2: 'B', 3: 'C', 4: 'D'}[n2]
print(f'  → {a88}')

print('=' * 70)
print('第89题  2023年 五一公路日均 比 元旦公路日均 多几倍')
w = base('五一假期', '公路')
y = base('元旦假期', '公路')
r89 = w / y
print(f'  五一 {V["五一假期"]["公路"]}/1.021 = {w:.3f}；元旦 {V["元旦假期"]["公路"]}/1.461 = {y:.3f}')
print(f'  是 {r89:.4f} 倍，多 {r89-1:.4f} 倍（2024年现期是 {V["五一假期"]["公路"]/V["元旦假期"]["公路"]:.3f} 倍）')
a89, dd = pick(r89 - 1, {'A': 16.7, 'B': 15.7, 'C': 13.9, 'D': 12.9})
print(f'  → {a89}  偏差 {dd}（C项13.9为“是……倍”）')

print('=' * 70)
print('第90题  逐项判断')
p = '国庆假期'
tot_daily = V[p]['总量'] / DAYS[p]
b_tot = tot_daily / (1 + G[p]['总量'])
b_road = b_tot - sum(base(p, k) for k in ['铁路', '民航', '水路'])
g_road = V[p]['公路'] / b_road - 1
b_tot2 = sum(V[p][k] for k in MODES) / (1 + G[p]['总量'])      # 用四项日均之和作现期
g_road2 = V[p]['公路'] / (b_tot2 - sum(base(p, k) for k in ['铁路', '民航', '水路'])) - 1
print(f'  A 铁路6.3%、民航11.1%、水路10.0%均高于合计3.9%，由混合增速公路必低于3.9%；')
print(f'    精确反推公路增速 {g_road*100:.3f}%（以四项日均和为现期：{g_road2*100:.3f}%）→ 对')
dB_daily = V['清明假期']['公路'] - V['端午假期']['公路']
dB_total = V['清明假期']['公路'] * DAYS['清明假期'] - V['端午假期']['公路'] * DAYS['端午假期']
print(f'  B 公路日均差 {dB_daily:.1f} 万人次；公路客流量（3天）差 {dB_total:.1f} 万人次 ≠ 3327 → 错')
cmp = {k: (V['春运期间'][k], V['清明假期'][k], V['春运期间'][k] < V['清明假期'][k]) for k in MODES}
print(f'  C 春运 vs 清明（是否小于）：{cmp} → 民航208.6>167.8，错')
p = '中秋假期'
sh = V[p]['水路'] / (V[p]['总量'] / DAYS[p]) * 100
sh2 = V[p]['水路'] / sum(V[p][k] for k in MODES) * 100
print(f'  D 中秋水路占比 = 66.0/(62956/3) = {sh:.4f}%（以四项和：{sh2:.4f}%），约0.3%而非3% → 错')

print('=' * 70)
print('本组答案：', {86: a86, 87: a87, 88: a88, 89: a89, 90: 'A'})
