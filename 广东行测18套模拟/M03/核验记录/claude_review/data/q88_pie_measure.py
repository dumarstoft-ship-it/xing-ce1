#!/usr/bin/env python3
"""Q88 pie-chart option measurement (M03 data-analysis review).

The option PNGs use a small, discrete palette:
  gray sector 95, black sector 33, checker = squares of 255 and a dark value
  (38 in option B, 0 in options A/C/D -- visually both black),
  white sector 255, sector outlines 58 (plus some anti-aliased values).
For each angle (0.1 deg steps, clockwise from 12 o'clock) the script samples
pixels along the radius (0.25R..0.92R) and classifies the angle as
  checker  if checker-dark pixels (0 or 38) are >= 15% of classified samples,
  else the majority of {95: gray, 33: black, 255: white}.
Outline (58) and anti-aliased pixels are ignored.  Sector shares are then
compared with the 2022 consumption shares in Table 2 of the visible material.

Usage: python3 q88_pie_measure.py [repo_root]
"""
import sys, math, json
from PIL import Image
import numpy as np

repo = sys.argv[1] if len(sys.argv) > 1 else '/home/user/xing-ce1'
base = repo + '/模考/2026下半年广东卷_16-33季_AI可读/assets/'
opts = {'A': 's25_p19_i02.png', 'B': 's25_p19_i03.png',
        'C': 's25_p20_i00.png', 'D': 's25_p20_i01.png'}

# 2022 consumption (表2, 万吨标准煤) read from the visible question file
qfile = repo + '/广东行测18套模拟/M03/题目.jsonl'
row = None
for line in open(qfile, encoding='utf-8'):
    d = json.loads(line)
    if d['number'] == 88:
        tabs = [b for m in d['materials'] for b in m['blocks'] if b['type'] == 'table']
        row = [r for r in tabs[1]['rows'] if r[0] == '2022'][0]
total, coal, oil, gas, other = [int(x) for x in row[1:]]
names = ['原煤(灰)', '原油(黑白格)', '天然气(白)', '其他(黑)']
exp = dict(zip(names, [coal / total, oil / total, gas / total, other / total]))
print('表2 2022年消费: 总量 %d = %d+%d+%d+%d (分项和 %d)' % (total, coal, oil, gas, other, coal + oil + gas + other))
print('期望扇区: ' + '；'.join('%s %.2f%% (%.1f°)' % (k, v * 100, v * 360) for k, v in exp.items()))
print()

cls_name = {'gray': '原煤(灰)', 'checker': '原油(黑白格)', 'white': '天然气(白)', 'black': '其他(黑)'}
results = {}
for key, f in opts.items():
    a = np.array(Image.open(base + f).convert('L')).astype(int)
    ys, xs = np.where(a < 200)
    cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
    R = ((xs.max() - xs.min()) + (ys.max() - ys.min())) / 4
    nstep = 3600
    labels = []
    for i in range(nstep):
        th = 2 * math.pi * i / nstep
        c = {95: 0, 33: 0, 38: 0, 255: 0}  # 38 also collects value 0
        r = 0.25 * R
        while r <= 0.92 * R:
            x = int(round(cx + r * math.sin(th)))
            y = int(round(cy - r * math.cos(th)))
            v = a[y, x]
            if v == 0:
                v = 38
            if v in c:
                c[v] += 1
            r += 0.5
        n = sum(c.values())
        if n == 0:
            labels.append(None); continue
        if c[38] >= 0.15 * n:
            labels.append('checker')
        else:
            labels.append({95: 'gray', 33: 'black', 255: 'white'}[max((95, 33, 255), key=lambda k: c[k])])
    # fill unclassified angles from nearest neighbour
    for i in range(nstep):
        if labels[i] is None:
            labels[i] = labels[i - 1]
    counts = {k: labels.count(k) for k in cls_name}
    bounds = [(i / 10, labels[i - 1], labels[i]) for i in range(nstep) if labels[i] != labels[i - 1]]
    print('选项 %s (%s): 圆心(%.1f,%.1f) R=%.1fpx  边界(度,从12点顺时针): %s' % (
        key, f, cx, cy, R, ', '.join('%.1f %s→%s' % b for b in bounds)))
    sq = 0.0
    res = {}
    for c_, nm in cls_name.items():
        share = counts[c_] / nstep
        res[nm] = share
        dev = (share - exp[nm]) * 100
        sq += dev ** 2
        print('   %-12s 实测 %6.2f%% (%5.1f°)  期望 %6.2f%%  偏差 %+6.2f 个百分点' % (nm, share * 100, share * 360, exp[nm] * 100, dev))
    print('   均方根偏差 %.2f 个百分点；天然气/其他 实测比 %.2f（期望 %.2f）；原油/其他 实测比 %.2f（期望 %.2f）' % (
        math.sqrt(sq / 4), res['天然气(白)'] / res['其他(黑)'], gas / other, res['原油(黑白格)'] / res['其他(黑)'], oil / other))
    results[key] = res
    print()
best = min(results, key=lambda k: sum((results[k][n] - exp[n]) ** 2 for n in names))
print('最接近的选项:', best)
