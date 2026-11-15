#!/usr/bin/env python3
"""第35题重建图排版修正原型（只写本脚本所在目录，不碰仓库）。

与编辑 编辑底稿/quant_data_make.py 第44-62行同一画法（720x180 画布 x3、圆心间距180、
线宽5px、DejaVu Serif、anchor='mm'），只改变文字水平偏移 dx、垂直偏移 dy、字号与半径 r，
测量每个数字字形到两条直径和圆周的最小像素间距。

输出：
  q35_fix_prototype.json            各参数组合的最小间距（含现行参数 dx=29,dy=28,font=28,r=70）
  q35_fix_candidate_r70.png         保留 r=70 版式的推荐参数（font=24, dx=±32, dy=±22）
  q35_fix_candidate_r70_print.png   上图按150mm宽、300dpi缩放的打印预览
  q35_fix_candidate.png             全搜索中间距最大的参数（需把 r 放大到84）
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
VALS = [['25', '3', '7', '−4'], ['14', '8', '6', '34'], ['51', '9', '4', '−15'], ['22', '8', '7', '?']]
SCALE = 3


def draw(dx, fs, r, dy):
    im = Image.new('RGB', (720 * SCALE, 180 * SCALE), 'white')
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(FONT, fs * SCALE)
    for j, vs in enumerate(VALS):
        cx, cy = 90 + j * 180, 90
        d.ellipse(((cx - r) * SCALE, (cy - r) * SCALE, (cx + r) * SCALE, (cy + r) * SCALE), outline='black', width=5)
        d.line(((cx - r) * SCALE, cy * SCALE, (cx + r) * SCALE, cy * SCALE), fill='black', width=5)
        d.line((cx * SCALE, (cy - r) * SCALE, cx * SCALE, (cy + r) * SCALE), fill='black', width=5)
        for v, sx, sy in zip(vs, [-1, 1, -1, 1], [-1, -1, 1, 1]):
            d.text(((cx + sx * dx) * SCALE, (cy + sy * dy) * SCALE), v, font=font, fill='black', anchor='mm')
    return im


def clearance(im, r):
    a = np.array(im.convert('L')) < 128
    lw = 1.8 * SCALE
    out = []
    for j, vs in enumerate(VALS):
        X, Y, R = (90 + j * 180) * SCALE, 90 * SCALE, r * SCALE
        for v, sx, sy in zip(vs, [-1, 1, -1, 1], [-1, -1, 1, 1]):
            x0, x1 = (X, X + R) if sx > 0 else (X - R, X)
            y0, y1 = (Y, Y + R) if sy > 0 else (Y - R, Y)
            ys, xs = np.nonzero(a[int(y0):int(y1), int(x0):int(x1)])
            ys, xs = ys + int(y0), xs + int(x0)
            g = (np.abs(xs - X) > lw) & (np.abs(ys - Y) > lw) & (np.abs(np.hypot(xs - X, ys - Y) - R) > lw)
            gx, gy = xs[g], ys[g]
            to_line = float(min(np.min(np.abs(gx - X)), np.min(np.abs(gy - Y))) - lw / 2)
            to_circle = float(np.min(R - np.hypot(gx - X, gy - Y)) - lw / 2)
            out.append({'text': v, 'circle': j + 1, 'to_diameter_px': round(to_line, 1), 'to_circle_px': round(to_circle, 1)})
    return out


def summarize(dx, fs, r, dy):
    c = clearance(draw(dx, fs, r, dy), r)
    return {'dx': dx, 'font': fs, 'r': r, 'dy': dy,
            'min_to_diameter_px': min(x['to_diameter_px'] for x in c),
            'min_to_circle_px': min(x['to_circle_px'] for x in c),
            'cell_minus15': [x for x in c if x['text'] == '−15'][0]}


current = summarize(29, 28, 70, 28)
print('现行参数(dx=29,dy=28,font=28,r=70):', current)
grid = []
for r in [70, 74, 78, 80, 84]:
    for fs in [24, 26, 28]:
        for dx in range(30, 44):
            for dy in [22, 24, 26, 28]:
                s = summarize(dx, fs, r, dy)
                s['min_clearance'] = min(s['min_to_diameter_px'], s['min_to_circle_px'])
                grid.append(s)
grid.sort(key=lambda s: -s['min_clearance'])
r70 = [s for s in grid if s['r'] == 70][:3]
print('保留 r=70 的前三组:', r70)
print('全搜索最佳:', grid[0])
rec = summarize(32, 24, 70, 22)
print('推荐(保留版式) dx=32,dy=22,font=24,r=70:', rec)
im = draw(32, 24, 70, 22)
im.save(OUT / 'q35_fix_candidate_r70.png')
w = round(150 / 25.4 * 300)
im.resize((w, round(w * im.height / im.width)), Image.LANCZOS).save(OUT / 'q35_fix_candidate_r70_print.png')
b = grid[0]
draw(b['dx'], b['font'], b['r'], b['dy']).save(OUT / 'q35_fix_candidate.png')
json.dump({'current': current, 'recommended_keep_r70': rec, 'r70_top3': r70, 'overall_top8': grid[:8]},
          open(OUT / 'q35_fix_prototype.json', 'w'), ensure_ascii=False, indent=1)
