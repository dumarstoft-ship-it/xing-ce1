# -*- coding: utf-8 -*-
"""第90题：量出四个选项饼图各扇区的角度，与由材料算出的各年占比对照。

做法：在饼图区域找圆心和半径，沿0.25°一步的射线在0.35R—0.85R之间取像素，
按“深色（移动数据流量，黑）/中灰（新兴业务，灰）/网点（其他，黑白相间）”分类，
统计每类所占角度。扇区之间的白缝按两侧均分。
"""
import numpy as np
from PIL import Image

BASE = '/home/user/xing-ce1/广东/行测/2022-2026/assets/GD2023-XJ/'
FIGS = {'A': ('GD2023-XJ-p29-i01.png', 2019), 'B': ('GD2023-XJ-p30-i01.png', 2020),
        'C': ('GD2023-XJ-p30-i02.png', 2021), 'D': ('GD2023-XJ-p30-i03.png', 2022)}


def find_circle(g):
    # 只看左侧饼图区域（图例在 x>680 处）
    sub = g[150:, :680]
    mask = sub < 200
    ys, xs = np.nonzero(mask)
    # 去掉边框线：边框在图片最外沿，饼图区域内只取远离边缘的点
    keep = (xs > 20) & (ys < sub.shape[0] - 20)
    ys, xs = ys[keep], xs[keep]
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 150
    r = ((x1 - x0) + (y1 - y0)) / 4
    return cx, cy, r


def classify(vals):
    vals = np.asarray(vals, dtype=float)
    dark = np.mean(vals < 70)
    mid = np.mean((vals >= 110) & (vals <= 205))
    light = np.mean(vals > 225)
    if dark > 0.85:
        return 'black'
    if mid > 0.75:
        return 'gray'
    if light > 0.85:
        return 'gap'
    return 'dots'


def measure(path):
    g = np.asarray(Image.open(path).convert('L'), dtype=float)
    cx, cy, r = find_circle(g)
    counts = {}
    seq = []
    for k in range(1440):
        th = np.deg2rad(k * 0.25)
        rs = np.linspace(0.35 * r, 0.85 * r, 60)
        xs = (cx + rs * np.sin(th)).round().astype(int)
        ys = (cy - rs * np.cos(th)).round().astype(int)
        c = classify(g[ys, xs])
        seq.append(c)
        counts[c] = counts.get(c, 0) + 1
    tot = sum(v for k2, v in counts.items() if k2 != 'gap')
    shares = {k2: v / tot for k2, v in counts.items() if k2 != 'gap'}
    return (cx, cy, r), counts, shares, seq


def boundaries(seq):
    out = []
    for i in range(len(seq)):
        if seq[i] != seq[i - 1]:
            out.append((i * 0.25, seq[i - 1], seq[i]))
    return out


def main_slices(seq, step=0.25, min_deg=4.0):
    """把边缘的抗锯齿杂点和白缝并入两侧扇区：长度<4°的段视为缝，从缝的中点切开。"""
    n = len(seq)
    # 旋转到某个段的起点，避免首尾相接的段被切开
    start = next(i for i in range(n) if seq[i] != seq[i - 1])
    s = seq[start:] + seq[:start]
    runs = []
    for i, c in enumerate(s):
        if runs and runs[-1][0] == c:
            runs[-1][2] += 1
        else:
            runs.append([c, i, 1])
    main = [r for r in runs if r[2] * step >= min_deg and r[0] != 'gap']
    # 合并相邻同类主段
    merged = []
    for r in main:
        if merged and merged[-1][0] == r[0]:
            merged[-1][2] = r[1] + r[2] - merged[-1][1]
        else:
            merged.append(list(r))
    cuts = []
    for k in range(len(merged)):
        a, b = merged[k], merged[(k + 1) % len(merged)]
        end_a = a[1] + a[2]
        beg_b = b[1] if b[1] >= end_a else b[1] + n
        cuts.append(((end_a + beg_b) / 2) % n)
    ext = {}
    for k in range(len(merged)):
        lo, hi = cuts[k - 1], cuts[k]
        ext[merged[k][0]] = ext.get(merged[k][0], 0) + ((hi - lo) % n) * step
    angles = [round(((c + start) % n) * step, 1) for c in cuts]
    return ext, angles


# 由材料算出的各年占比
total2022 = 15800.0
rates = {2019: 0.005, 2020: 0.039, 2021: 0.081, 2022: 0.080}
tot = {2022: total2022}
for y in (2021, 2020, 2019, 2018):
    tot[y] = tot[y + 1] / (1 + rates[y + 1])
mobile = {2018: 5984, 2019: 6096, 2020: 6204, 2021: 6381, 2022: 6397}
new = {2018: 1084, 2019: 1374, 2020: 1737, 2021: 2372, 2022: 3072}

print('由材料推算的电信业务收入（亿元）：', {y: round(v, 1) for y, v in sorted(tot.items())})
print('2022年较2018年增加：', round(tot[2022] - tot[2018], 1))
for label, (fn, year) in FIGS.items():
    (cx, cy, r), counts, shares, seq = measure(BASE + fn)
    m, n = mobile[year] / tot[year], new[year] / tot[year]
    print('\n选项%s（%d年）圆心(%.0f,%.0f) 半径%.0f' % (label, year, cx, cy, r))
    ext, cuts = main_slices(seq)
    print('  图中量得（白缝从中点切开）：移动(黑)%.1f°=%.1f%%  新兴(灰)%.1f°=%.1f%%  其他(网点)%.1f°=%.1f%%' % (
        ext.get('black', 0), ext.get('black', 0) / 3.6, ext.get('gray', 0), ext.get('gray', 0) / 3.6,
        ext.get('dots', 0), ext.get('dots', 0) / 3.6))
    print('  切分角（度，自12点钟方向顺时针）：', cuts)
    print('  材料算得：移动%.1f%%  新兴%.1f%%  其他%.1f%%' % (100 * m, 100 * n, 100 * (1 - m - n)))
    print('  粗分类计数占比：移动%.1f%%  新兴%.1f%%  其他%.1f%%' % (
        100 * shares.get('black', 0), 100 * shares.get('gray', 0), 100 * shares.get('dots', 0)))
