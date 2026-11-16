#!/usr/bin/env python3
"""M01 资料分析第4组（第86—90题）：2023年9月—2024年8月中国装载机国内销量与出口量。

用法：python3 q86-90_m4_loader.py
两张表（原卷为统计图）直接从 ../../输入/data.json 读取，逐题精确计算。
"""
import json
import math
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / '输入' / 'data.json'
MID = 'gd-mock-2026h2-s16-m4'

d = json.loads(DATA.read_text(encoding='utf-8'))
m = next(m for m in d['materials'] if m['id'] == MID)
t_dom, t_exp = [b for b in m['blocks'] if b['type'] == 'table']
assert t_dom['title'].startswith('图1') and '国内销量' in t_dom['title']
assert t_exp['title'].startswith('图2') and '出口量' in t_exp['title']


def parse(tb):
    out = {}
    for mon, v, g in tb['rows']:
        out[mon] = (int(v), float(g.replace('−', '-')) / 100)
    return out


DOM, EXP = parse(t_dom), parse(t_exp)
MONTHS = [r[0] for r in t_dom['rows']]
assert MONTHS == [r[0] for r in t_exp['rows']]


def base(tbl, mon):
    v, g = tbl[mon]
    return v / (1 + g)


def inc(tbl, mon):
    v, g = tbl[mon]
    return v - v / (1 + g)


def pick(value, opts):
    diffs = {k: abs(value - v) for k, v in opts.items()}
    return min(diffs, key=diffs.get), diffs


print('=' * 70)
print('数据检查：12个月连续、无重叠年份，表内无法做同比交叉验证；仅列出推算的上年同月值看是否合理')
for mon in MONTHS:
    print(f'  {mon}: 国内{DOM[mon][0]:>5}（{DOM[mon][1]*100:+.1f}%，上年同月≈{base(DOM, mon):7.0f}）'
          f'  出口{EXP[mon][0]:>5}（{EXP[mon][1]*100:+.1f}%，上年同月≈{base(EXP, mon):7.0f}）'
          f'  合计{DOM[mon][0]+EXP[mon][0]:>6}')

print('=' * 70)
print('第86题  2024年8月国内外总销量同比增速')
mon = '2024-08'
cur_t = DOM[mon][0] + EXP[mon][0]
base_t = base(DOM, mon) + base(EXP, mon)
g86 = (cur_t / base_t - 1) * 100
trap = (DOM[mon][0] * DOM[mon][1] + EXP[mon][0] * EXP[mon][1]) / cur_t * 100
print(f'  现期合计={cur_t}；基期=4036/1.09+4293/1.218={base(DOM, mon):.2f}+{base(EXP, mon):.2f}={base_t:.2f}')
print(f'  增速={g86:.4f}%（误按现期量加权得{trap:.3f}%，即B项陷阱；两增速简单平均{(9.0+21.8)/2:.1f}%）')
ans86, diffs = pick(g86, {'A': 15.2, 'B': 15.6, 'C': 19.2, 'D': 22.6})
print('  偏差', {k: round(v, 4) for k, v in diffs.items()}, '→', ans86)
assert ans86 == 'A'

print('=' * 70)
print('第87题  2024年二季度国内销量与出口量之差')
q2 = ['2024-04', '2024-05', '2024-06']
sd, se = sum(DOM[x][0] for x in q2), sum(EXP[x][0] for x in q2)
diff87 = sd - se
print(f'  国内={"+".join(str(DOM[x][0]) for x in q2)}={sd}；出口={"+".join(str(EXP[x][0]) for x in q2)}={se}；差={diff87:+d}')
opts87 = {'A': 1399, 'B': -1399, 'C': 1157, 'D': -1157}
ans87 = next(k for k, v in opts87.items() if v == diff87)
print('  →', ans87)
assert ans87 == 'C'

print('=' * 70)
print('第88题  2023年9—12月国内销量月均增长率')
v0, v3 = DOM['2023-09'][0], DOM['2023-12'][0]
g3 = ((v3 / v0) ** (1 / 3) - 1) * 100
g4 = ((v3 / v0) ** (1 / 4) - 1) * 100
print(f'  9月{v0}→12月{v3}，共3个间隔：(5599/4237)^(1/3)-1 = {(v3/v0):.5f}^(1/3)-1 = {g3:.4f}%')
print(f'  （误按4个间隔：{g4:.3f}%，接近C项7%）')
for k, x in {'A': 13, 'B': 10, 'C': 7, 'D': 4}.items():
    print(f'    检验 {k}项 {x}%：{v0}×(1+{x}%)^3 = {v0*(1+x/100)**3:.1f}')
ans88, diffs = pick(g3, {'A': 13, 'B': 10, 'C': 7, 'D': 4})
print('  偏差', {k: round(v, 3) for k, v in diffs.items()}, '→', ans88)
assert ans88 == 'B'

print('=' * 70)
print('第89题  2022年9月国内外总销量')
mon = '2023-09'
v89 = base(DOM, mon) + base(EXP, mon)
print(f'  4237/(1-24.2%)+3452/(1-15.4%) = {base(DOM, mon):.3f}+{base(EXP, mon):.3f} = {v89:.3f}台')
ans89, diffs = pick(v89, {'A': 7689, 'B': 8582, 'C': 9670, 'D': 10117})
print('  偏差', {k: round(v, 2) for k, v in diffs.items()}, '→', ans89)
assert ans89 == 'C'

print('=' * 70)
print('第90题  表述正确的是')
m24 = [x for x in MONTHS if x.startswith('2024')]
moreA = [x for x in m24 if DOM[x][0] > EXP[x][0]]
print(f'  A: 2024年1—8月国内>出口的月份：{moreA}，共{len(moreA)}个 → {"对" if len(moreA) == 5 else "错"}')
h1 = ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06']
same = []
for x in h1:
    prev = MONTHS[MONTHS.index(x) - 1]
    yoy = EXP[x][1]
    mom = EXP[x][0] - EXP[prev][0]
    s = (yoy > 0) == (mom > 0)
    if s:
        same.append(x)
    print(f'     B: {x} 同比{yoy*100:+.1f}%  环比{EXP[x][0]}-{EXP[prev][0]}={mom:+d}  趋势相同：{s}')
print(f'  B: 趋势相同的月份 {same}，共{len(same)}个 → {"对" if len(same) == 5 else "错"}')
fast = max(MONTHS, key=lambda x: EXP[x][1])
incs = {x: inc(EXP, x) for x in MONTHS}
big = max(MONTHS, key=lambda x: incs[x])
print(f'  C: 出口同比增速最快={fast}（{EXP[fast][1]*100:.1f}%，增量{incs[fast]:.1f}台）；'
      f'同比增量最大={big}（{incs[big]:.1f}台） → {"对" if fast == big else "错"}')
top = sorted(incs.items(), key=lambda kv: -kv[1])[:4]
print('     出口同比增量前四：', [(k, round(v, 1)) for k, v in top])
q4 = ['2023-10', '2023-11', '2023-12']
sd4, se4 = sum(DOM[x][0] for x in q4), sum(EXP[x][0] for x in q4)
avg_gap = (sd4 - se4) / 3
print(f'  D: 2023年四季度 国内{sd4} 出口{se4}，月均差=({sd4}-{se4})/3={avg_gap:.2f}台 → '
      f'{"对" if avg_gap > 1400 else "错"}')
assert len(moreA) != 5 and len(same) != 5 and fast != big and avg_gap > 1400
ans90 = 'D'
print('  →', ans90)

print('=' * 70)
print('第4组答案：', {86: ans86, 87: ans87, 88: ans88, 89: ans89, 90: ans90})
