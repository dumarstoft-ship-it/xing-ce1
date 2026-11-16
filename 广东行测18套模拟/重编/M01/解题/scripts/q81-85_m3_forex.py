#!/usr/bin/env python3
"""M01 资料分析第3组（第81—85题）：2024年广东省外汇管理与外贸外资。

用法：python3 q81-85_m3_forex.py
材料原文和选项从 ../../输入/data.json 读取：材料理解题逐项检查选项文字是否出现在原文（及出现在哪一段），
计算题按材料数字精确计算。
"""
import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / '输入' / 'data.json'
MID = 'gd-mock-2026h2-s16-m3'

d = json.loads(DATA.read_text(encoding='utf-8'))
m = next(m for m in d['materials'] if m['id'] == MID)
text = ''.join(b['text'] for b in m['blocks'] if b['type'] == 'text')
Q = {q['number']: q for q in d['questions'] if q['material_id'] == MID}


def opt(n, k):
    return ''.join(p['text'] for p in Q[n]['options'][k])


def pick(value, opts):
    diffs = {k: abs(value - v) for k, v in opts.items()}
    return min(diffs, key=diffs.get), diffs


for frag in ['外贸进出口9.1万亿元，同比增长9.8%，对全国增长贡献率达38.7%',
             '跨境资金流动规模突破2万亿美元大关、达到2.3万亿美元，同比增长16.1%',
             '新型离岸国际贸易跨境收支154亿美元，同比增长18.2%',
             '已有103家主办企业', '惠及境内外企业1213家',
             '累计10家企业取得QFLP试点资格，5家企业取得QDLP试点资格',
             '由南沙自贸区扩围至广东省全辖']:
    assert frag in text, frag

i_trade = text.index('在稳外贸方面')
i_inv = text.index('在稳外资方面')


def where(s):
    if s not in text:
        return '原文无'
    i = text.index(s)
    if i < i_trade:
        return '首段总述'
    return '稳外贸部分' if i < i_inv else '稳外资部分'


print('=' * 70)
print('数据自洽检查')
base_flow = 2.3 / 1.161
print(f'  跨境资金流动：2023年=2.3/1.161={base_flow:.4f}万亿美元（<2，与“突破2万亿美元大关”一致；'
      f'2.3为一位小数，2023年取值区间约{2.25/1.161:.3f}～{2.35/1.161:.3f}）')
gd_inc = 9.1 * 0.098 / 1.098
print(f'  广东外贸增量={gd_inc:.4f}万亿元，推得全国增量={gd_inc/0.387:.4f}万亿元'
      '（与公开的2024年全国外贸增量约2.1万亿元量级一致）')
print(f'  网购跨境收支2023年={1215/1.264:.2f}亿美元；新型离岸贸易2023年={154/1.182:.2f}亿美元；无内部矛盾')

print('=' * 70)
print('第81题  不属于“组合拳”核心举措的是')
head = text[:i_trade]
for k in 'ABCD':
    s = opt(81, k)
    print(f'  {k}. {s} → {"首段原文有" if s in head else "首段原文无"}')
ans81 = [k for k in 'ABCD' if opt(81, k) not in head]
assert ans81 == ['D']
ans81 = ans81[0]
print('  →', ans81)

print('=' * 70)
print('第82题  “科汇通”试点主要内容')
seg = text[text.index('科汇通'):]
seg = seg[:seg.index('三是')]
print('  原文：', seg)
for k in 'ABCD':
    s = opt(82, k)
    core = s.rstrip('。')
    print(f'  {k}. 出现位置：{where(core)}；在“科汇通”一句中：{core in seg}')
ans82 = [k for k in 'ABCD' if opt(82, k).rstrip('。') in seg]
assert ans82 == ['A']
ans82 = ans82[0]
print('  →', ans82)

print('=' * 70)
print('第83题  2024年全国外贸进出口增长量')
v83 = gd_inc / 0.387
ans83, diffs = pick(v83, {'A': 1.8, 'B': 2.1, 'C': 2.4, 'D': 2.7})
print(f'  广东增量=9.1×9.8%/(1+9.8%)={gd_inc:.4f}；全国增量=广东增量/38.7%={v83:.4f}万亿元；偏差',
      {k: round(v, 4) for k, v in diffs.items()}, '→', ans83)
assert ans83 == 'B'

print('=' * 70)
print('第84题  2023年新型离岸国际贸易跨境收支')
v84 = 154 / 1.182
ans84, diffs = pick(v84, {'A': 125, 'B': 130, 'C': 135, 'D': 140})
print(f'  154/(1+18.2%)={v84:.4f}亿美元；偏差', {k: round(v, 3) for k, v in diffs.items()}, '→', ans84)
assert ans84 == 'B'

print('=' * 70)
print('第85题  说法正确的是')
print(f'  A: 原文含“首次”吗？{"首次" in text}；原文仅说“突破2万亿美元大关”，未说“首次”，'
      f'更早年份无数据 → 无法推出（2023年推算为{base_flow:.3f}万亿美元，也只说明上一年未达2万亿）')
rB = 103 / 1213
print(f'  B: 103/1213 = {rB*100:.3f}% → {"对" if rB > 0.10 else "错（不足10%）"}')
print(f'  C: 原文为“扩围至广东省全辖”，“推广至全国范围”出现在原文吗？{"全国范围" in text} → 错')
rD = 10 / 5
print(f'  D: 10/5 = {rD} 倍 → {"对" if rD == 2 else "错"}')
assert '首次' not in text and rB < 0.10 and '全国范围' not in text and rD == 2
ans85 = 'D'
print('  →', ans85)

print('=' * 70)
print('第3组答案：', {81: ans81, 82: ans82, 83: ans83, 84: ans84, 85: ans85})
