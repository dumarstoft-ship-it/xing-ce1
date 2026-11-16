#!/usr/bin/env python3
"""M01 资料分析第2组（第76—80题）：企业发明专利产业化平均收益与产业化率。

用法：python3 q76-80_m2_patent.py
文字材料中的数字先断言确实出现在 ../../输入/data.json 的材料原文中，表格直接从 data.json 读取。
"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / '输入' / 'data.json'
MID = 'gd-mock-2026h2-s16-m2'

d = json.loads(DATA.read_text(encoding='utf-8'))
m = next(m for m in d['materials'] if m['id'] == MID)
text = next(b['text'] for b in m['blocks'] if b['type'] == 'text')
tb = next(b for b in m['blocks'] if b['type'] == 'table')

for frag in ['平均收益金额为829.6万元/件，较上年增长3.8%', '自2021年以来连续两年提高',
             '内资企业发明专利产业化平均收益金额为811.4万元/件，分别较港澳台投资企业以及外商投资企业低20.9%和26.4%',
             '较内资企业整体平均水平高6.8%，较其他内资企业高22.7%',
             '产业化率达到51.3%，较上年提高3.2个百分点',
             '大型企业数量占全国的比重为18.2%，中型企业数量占比为23.9%，小型企业数量占比为37.9%']:
    assert frag in text, frag

AVG23, G23 = 829.6, 0.038
DOM = 811.4
LOW_HMT, LOW_FOR = 0.209, 0.264
PRIV_OVER_DOM, PRIV_OVER_OTHER = 0.068, 0.227
RATE23, RATE_UP = 51.3, 3.2

YEARS = tb['headers'][1:]
R = {row[0]: [float(x.rstrip('%')) for x in row[1:]] for row in tb['rows']}


def pick(value, opts):
    diffs = {k: abs(value - v) for k, v in opts.items()}
    return min(diffs, key=diffs.get), diffs


print('=' * 70)
print('数据自洽检查')
hmt = DOM / (1 - LOW_HMT)
foreign = DOM / (1 - LOW_FOR)
priv = DOM * (1 + PRIV_OVER_DOM)
other = priv / (1 + PRIV_OVER_OTHER)
w_priv = (DOM - other) / (priv - other)
print(f'  港澳台={hmt:.2f}  外商={foreign:.2f}  内资={DOM}  全部企业={AVG23}'
      f' → 全部企业均值介于内资与外资之间：{DOM < AVG23 < min(hmt, foreign)}')
print(f'  民营={priv:.2f}  其他内资={other:.2f}  → 内资整体{DOM}介于两者之间，'
      f'隐含民营专利件数占内资约{w_priv*100:.1f}%（0~100%内即自洽）')
rate22 = RATE23 - RATE_UP
for i, y in enumerate(YEARS):
    vals = [R[k][i] for k in R]
    print(f'  {y}: 各规模 {vals}', end='')
    if y == '2023年':
        print(f'；全国{RATE23}%在[{min(vals)},{max(vals)}]内：{min(vals) <= RATE23 <= max(vals)}')
    elif y == '2022年':
        print(f'；全国{rate22:.1f}%在[{min(vals)},{max(vals)}]内：{min(vals) <= rate22 <= max(vals)}')
    else:
        print()
micro_share = 100 - 18.2 - 23.9 - 37.9
w = {'大型企业': 18.2, '中型企业': 23.9, '小型企业': 37.9, '微型企业': micro_share}
wavg23 = sum(w[k] * R[k][-1] for k in w) / 100
print(f'  企业数量占比：微型=100-18.2-23.9-37.9={micro_share:.1f}%；'
      f'以企业数量占比加权的2023年产业化率={wavg23:.2f}%（全国51.3%按专利件数加权，口径不同，不构成矛盾）')

print('=' * 70)
print('第76题  2024年平均收益（保持3.8%增速）')
v76 = AVG23 * (1 + G23)
ans76, diffs = pick(v76, {'A': 861.1, 'B': 865.7, 'C': 870.2, 'D': 874.5})
print(f'  829.6×1.038 = {v76:.4f}；偏差', {k: round(v, 3) for k, v in diffs.items()}, '→', ans76)
assert ans76 == 'A'

print('=' * 70)
print('第77题  2023年较2021年的间隔增长率')
v77 = ((1 + G23) * (1 + 0.029) - 1) * 100
ans77, diffs = pick(v77, {'A': 6.5, 'B': 6.7, 'C': 6.8, 'D': 7.0})
print(f'  3.8%+2.9%+3.8%×2.9% = {v77:.4f}%；偏差', {k: round(v, 4) for k, v in diffs.items()}, '→', ans77)
assert ans77 == 'C'

print('=' * 70)
print('第78题  港澳台投资企业比外商投资企业高/低多少')
d78 = hmt - foreign
print(f'  港澳台=811.4/(1-20.9%)={hmt:.3f}；外商=811.4/(1-26.4%)={foreign:.3f}；差={d78:+.3f}万元/件')
trap = DOM * (1 + LOW_HMT) - DOM * (1 + LOW_FOR)
print(f'  （误用“811.4×(1+x%)”会得 {trap:+.3f}，落入A项“低不到70”）')
ans78 = ('B' if -d78 > 70 else 'A') if d78 < 0 else ('D' if d78 > 70 else 'C')
print('  →', ans78)
assert ans78 == 'B'

print('=' * 70)
print('第79题  除民营外的其他内资企业平均收益')
ans79, diffs = pick(other, {'A': 661.3, 'B': 689.2, 'C': 706.3, 'D': 721.5})
print(f'  811.4×1.068/1.227 = {priv:.4f}/1.227 = {other:.4f}；偏差',
      {k: round(v, 3) for k, v in diffs.items()}, '→', ans79)
assert ans79 == 'C'

print('=' * 70)
print('第80题  选出“不正确”的表述')
okA = True
for k in R:
    q = R[k][-1] / R[k][0]
    okA = okA and q >= 1.2
    print(f'  A: {k} 2023/2019 = {R[k][-1]}/{R[k][0]} = {q:.4f}')
print('     → A', '正确' if okA else '不正确（大型企业不足1.2倍）')
dS = R['小型企业'][-1] - R['小型企业'][-2]
dM = R['微型企业'][-1] - R['微型企业'][-2]
okB = abs(dS - 8.6) < 1e-9 and abs(dM - 11.8) < 1e-9
print(f'  B: 小型 {dS:.1f}个百分点，微型 {dM:.1f}个百分点 → {"正确" if okB else "不正确"}')
okC = abs(rate22 - 48.1) < 1e-9
print(f'  C: 51.3-3.2 = {rate22:.1f}% → {"正确" if okC else "不正确"}')
gaps = [R['中型企业'][i] - R['小型企业'][i] for i in (1, 2, 3)]
okD = gaps[0] < gaps[1] < gaps[2]
print(f'  D: 2020—2022年中型-小型差值 = {[round(g, 1) for g in gaps]} → {"正确" if okD else "不正确"}')
assert (not okA) and okB and okC and okD
ans80 = 'A'
print('  →', ans80)

print('=' * 70)
print('第2组答案：', {76: ans76, 77: ans77, 78: ans78, 79: ans79, 80: ans80})
