#!/usr/bin/env python3
"""M03 资料分析第2组（第76—80题）：再生资源回收与废弃电器电子产品回收。

用法：python3 q76-80_m2_recycle.py
文字数据按材料抄录（见下方常量），表格从 ../../输入/data.json 读取，逐题精确计算。
"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / '输入' / 'data.json'
MID = 'gd-mock-2026h2-s18-m2'

d = json.loads(DATA.read_text(encoding='utf-8'))
m = next(m for m in d['materials'] if m['id'] == MID)
text = m['blocks'][0]['text']
tb = m['blocks'][1]
T = {int(r[0]): (float(r[1]), float(r[2]), float(r[3])) for r in tb['rows']}  # 年: (万台, 万吨, 亿元)

# 文字材料（十个品种再生资源）
W23, gW23, dgW = 3.76, 0.015, 0.041        # 亿吨；2023增速；增速比上年提高4.1个百分点
A23, gA23, dgA = 1.3, -0.012, 0.028        # 万亿元；2023增速；降幅比上年收窄2.8个百分点
for s in ['3.76亿吨', '增长1.5%', '提高4.1个百分点', '1.3万亿元', '下降1.2%', '收窄2.8个百分点']:
    assert s in text, s
gW22 = gW23 - dgW            # 2022年重量增速
gA22 = gA23 - dgA            # 2022年金额增速：降幅1.2%+2.8%=4.0%
W22, W21 = W23 / (1 + gW23), W23 / (1 + gW23) / (1 + gW22)
A22, A21 = A23 / (1 + gA23), A23 / (1 + gA23) / (1 + gA22)


def pick(value, opts):
    diffs = {k: abs(value - v) for k, v in opts.items()}
    return min(diffs, key=diffs.get), diffs


print('=' * 70)
print('数据整理与自洽检查')
print(f'  2022年重量增速 = 1.5% − 4.1% = {gW22*100:.1f}%；2022年金额增速 = −(1.2%+2.8%) = {gA22*100:.1f}%')
print(f'  十品种重量：2021 {W21:.4f}、2022 {W22:.4f}、2023 {W23} 亿吨')
print(f'  十品种金额：2021 {A21:.4f}、2022 {A22:.4f}、2023 {A23} 万亿元')
print(f'  废弃电器电子产品2023年占十品种：重量 {T[2023][1]/(W23*1e4)*100:.2f}%，金额 {T[2023][2]/(A23*1e4)*100:.2f}%（部分小于整体，无矛盾）')
for y in (2021, 2022, 2023):
    g = [(T[y][i] / T[y - 1][i] - 1) * 100 for i in range(3)]
    print(f'  废弃电器 {y} 同比：数量 {g[0]:+.2f}%  重量 {g[1]:+.2f}%  金额 {g[2]:+.2f}%')

print('=' * 70)
print('第76题  十品种平均每吨回收金额 2023 比 2021')
avg23 = A23 * 1e12 / (W23 * 1e8)
avg21 = A21 * 1e12 / (W21 * 1e8)
r76 = ((1 + gA23) * (1 + gA22)) / ((1 + gW23) * (1 + gW22)) - 1
print(f'  2023均值 {avg23:.2f} 元/吨，2021均值 {avg21:.2f} 元/吨，变化 {(avg23/avg21-1)*100:.3f}%')
print(f'  公式：(1−1.2%)(1−4.0%)/[(1+1.5%)(1−2.6%)] − 1 = 0.94848/0.98861 − 1 = {r76*100:.3f}%')
gA_int = (1 + gA23) * (1 + gA22) - 1
gW_int = (1 + gW23) * (1 + gW22) - 1
print(f'  金额间隔增速 {gA_int*100:.3f}%，重量间隔增速 {gW_int*100:.3f}%；(a−b)/(1+b) = {(gA_int-gW_int)/(1+gW_int)*100:.3f}%')
a76, dd = pick(r76 * 100, {'A': -5.6, 'B': 5.6, 'C': -4.1, 'D': 4.1})
print(f'  → {a76}  偏差 {dd}')

print('=' * 70)
print('第77题  2022年 数量/重量/金额 同比降幅超过10%的项数')
g22 = {k: (T[2022][i] / T[2021][i] - 1) * 100 for i, k in enumerate(['数量', '重量', '金额'])}
print('  ', {k: round(v, 3) for k, v in g22.items()})
n77 = sum(1 for v in g22.values() if v < -10)
print(f'  降幅超过10%的有 {n77} 项 → {"ABCD"[n77]}')
a77 = 'ABCD'[n77]

print('=' * 70)
print('第78题  平均每台回收金额 2021 比 2020（元/台 = 亿元×1e8 / (万台×1e4)）')
per = {y: T[y][2] * 1e8 / (T[y][0] * 1e4) for y in T}
v78 = per[2021] - per[2020]
print(f'  2020 {per[2020]:.3f} 元/台，2021 {per[2021]:.3f} 元/台，差 {v78:+.3f} 元')
a78, dd = pick(v78, {'A': 26, 'B': -26, 'C': 62, 'D': -62})
print(f'  → {a78}  偏差 {dd}')

print('=' * 70)
print('第79题  平均每吨回收金额 > 5000元 的年份数（元/吨 = 亿元×1e8 / (万吨×1e4)）')
pt = {y: T[y][2] * 1e8 / (T[y][1] * 1e4) for y in T}
print('  ', {y: round(v, 2) for y, v in pt.items()})
n79 = sum(1 for v in pt.values() if v > 5000)
a79 = {4: 'A', 3: 'B', 2: 'C', 1: 'D'}[n79]
print(f'  超过5000元的有 {n79} 个 → {a79}')

print('=' * 70)
print('第80题  逐项判断')
sw = sum(T[y][1] for y in T)
print(f'  A 2020—2023回收重量合计 {sw:.0f} 万吨（不到1700？{sw < 1700}）→ 错')
ymin_n = min(T, key=lambda y: T[y][0])
ymin_w = min(T, key=lambda y: T[y][1])
print(f'  B 数量最少 {ymin_n} 年，重量最少 {ymin_w} 年 → {"对" if ymin_n == ymin_w else "错"}')
print(f'  C 2021年十品种重量 = 3.76/(1.015×0.974) = {W21:.4f} 亿吨（超过4亿？{W21 > 4}）→ 错')
gpart = T[2023][2] / T[2022][2] - 1
sh23 = T[2023][2] / (A23 * 1e4) * 100
sh22 = T[2022][2] / (A22 * 1e4) * 100
print(f'  D 废弃电器金额增速 {gpart*100:+.2f}% > 十品种金额增速 {gA23*100:+.1f}%，比重 {sh22:.4f}% → {sh23:.4f}%，上升 → 对')
a80 = 'D'

print('=' * 70)
print('本组答案：', {76: a76, 77: a77, 78: a78, 79: a79, 80: a80})
