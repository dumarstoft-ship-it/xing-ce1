#!/usr/bin/env python3
"""Print-size check for M03 Q66-Q70 figures.

For each figure, measures (in source pixels) the smallest legibility-critical
features, then converts them to millimetres at several candidate print widths.
Feature boxes were located by eye on enlarged crops; the pixel extents inside
each box are measured here from the image (dark-pixel bounding box), so the
numbers can be re-run and checked.

Rules of thumb used for the recommendation (A4 printed at 100%):
  * Chinese/Latin label glyph height  >= 2.5 mm  (~ 9-10 pt body text)
  * small digits on contour lines     >= 2.0 mm
  * stroke width                      >= 0.15 mm (thinner lines get lost in toner)
  * dash length / gap                 >= 0.6 mm / 0.35 mm, so a dashed line still reads as dashed
  * arrowhead length                  >= 1.2 mm
Run: python3 print_sizes.py
"""
from pathlib import Path

import numpy as np
from PIL import Image

REPO = Path('/home/user/xing-ce1')
FIG = {
    'Q66': REPO / '模考/2026下半年广东卷_16-33季_AI可读/assets/s23_p18_i00.png',
    'Q67': REPO / '模考/2026下半年广东卷_16-33季_AI可读/assets/s21_p17_i04.png',
    'Q69': REPO / '广东行测18套模拟/M03/assets/q69_foodweb.png',
    'Q70': REPO / '模考/2026下半年广东卷_16-33季_AI可读/assets/s26_p19_i01.png',
}

# (description, box x0,y0,x1,y1, what to measure: 'h' glyph height, 'w' extent width, 'stroke' line thickness)
FEATURES = {
    'Q66': [
        ('标签"甲"字高', (95, 135, 115, 157), 'h'),
        ('标签"乙"字高', (238, 135, 260, 157), 'h'),
        ('甲球露出液面部分高度', (88, 8, 118, 27), 'ball_above'),
        ('液体内短划线长度', (126, 31, 145, 36), 'w'),
        ('液面线粗细', (60, 20, 80, 33), 'stroke'),
    ],
    'Q67': [
        ('字母"A"字高', (755, 115, 805, 170), 'h'),
        ('字母"O"字高', (1200, 55, 1255, 110), 'h'),
        ('虚线单段长度(约)', (None,), 'svg_dash'),
        ('B落点低于墙角的距离', (None,), 'svg_drop'),
    ],
    'Q69': [
        ('生物名称字高(“蛇”)', (1600, 300, 1690, 370), 'h'),
        ('箭头头部长度(SVG: 9单位×3.06)', (None,), 'svg_arrow'),
        ('连线粗细', (250, 80, 340, 100), 'stroke'),
    ],
    'Q70': [
        ('等高线注记"600"(倾斜)外框高', (98, 12, 121, 41), 'h'),
        ('等高线注记"200"(左缘)字高', (12, 96, 42, 123), 'h'),
        ('圈码"②"高', (110, 86, 129, 105), 'h'),
        ('圈码"④"高', (316, 272, 335, 291), 'h'),
        ('"北"字高', (36, 18, 57, 37), 'h'),
        ('图例文字"区域界"字高', (300, 305, 350, 322), 'h'),
        ('等高线粗细(左缘300线)', (15, 70, 40, 92), 'stroke'),
        ('区域界虚线单段长度(沿弧)', (None,), 'q70_dash'),
        ('区域界虚线间隔(沿弧)', (None,), 'q70_gap'),
        ('指北针箭头总长', (10, 30, 38, 57), 'diag'),
    ],
}


def dark(img, thr=150):
    return np.array(img.convert('L')).astype(int) < thr


def measure(fig, box, kind, img):
    d = dark(img)
    if kind == 'svg_dash':
        # SVG viewBox 216 units wide, stroke-dasharray 3.2 1.8 ; return in px of the 1296-px PNG
        return 3.2 * 1296 / 216
    if kind == 'svg_arrow':
        return 9.0 * 3.06
    if kind == 'svg_drop':
        return (84 - 69) * 1296 / 216
    if kind in ('q70_dash', 'q70_gap'):
        # dashed 区域界 ellipse (centre ~(216.5,233), semi-axes ~(79,66)): walk its left half,
        # take the darkest pixel within +-3 px radially, and measure dark/light run lengths along the arc
        import math
        g = np.array(img.convert('L')).astype(int)
        cx, cy, ax, ay = 216.5, 233.0, 79.0, 66.0
        n = 3000
        ts = [math.radians(100 + 150 * i / n) for i in range(n)]
        seq = []
        for t in ts:
            best = 255
            for dr in np.linspace(-3, 3, 13):
                xi = int(round(cx + (ax + dr) * math.cos(t)))
                yi = int(round(cy - (ay + dr) * math.sin(t)))
                if 0 <= xi < g.shape[1] and 0 <= yi < g.shape[0]:
                    best = min(best, g[yi, xi])
            seq.append(best < 140)
        pts = [(cx + ax * math.cos(t), cy - ay * math.sin(t)) for t in ts]
        runs, cur_v, cur = [], seq[0], 0.0
        for i in range(n - 1):
            step = math.dist(pts[i], pts[i + 1])
            if seq[i] == cur_v:
                cur += step
            else:
                runs.append((cur_v, cur))
                cur_v, cur = seq[i], step
        runs = runs[1:]   # drop the partial first run
        want = kind == 'q70_dash'
        vals = [r for v, r in runs if v == want]
        return float(np.median(vals)) if vals else float('nan')
    x0, y0, x1, y1 = box
    sub = d[y0:y1, x0:x1]
    ys, xs = np.where(sub)
    if len(ys) == 0:
        return float('nan')
    if kind == 'h':
        return ys.max() - ys.min() + 1
    if kind == 'w':
        return xs.max() - xs.min() + 1
    if kind == 'diag':
        return float(np.hypot(xs.max() - xs.min(), ys.max() - ys.min()))
    if kind == 'stroke':
        # median vertical run length of dark pixels per column
        runs = []
        for c in range(sub.shape[1]):
            col = sub[:, c]
            r = 0
            for v in col:
                if v:
                    r += 1
                elif r:
                    runs.append(r)
                    r = 0
            if r:
                runs.append(r)
        return float(np.median(runs)) if runs else float('nan')
    if kind == 'ball_above':
        g = np.array(img.convert('L')).astype(int)
        fill = np.abs(g[y0:y1, x0:x1] - 178) <= 8
        ys2, _ = np.where(fill)
        return (26 - (ys2.min() + y0)) if len(ys2) else float('nan')
    raise ValueError(kind)


WIDTHS = {'Q66': [55, 60, 67.3, 75], 'Q67': [42.5, 60, 70, 75], 'Q69': [90, 100, 110, 120], 'Q70': [80, 98.1, 110, 120]}
# 67.3 mm / 42.5 mm / 98.1 mm are the source-PDF print widths (图片清单.json bbox_pt);
# 70 mm is the width already registered for Q67 in 打印排版/题图尺寸调整.json;
# 120 mm is where build_print.py caps the editor-made Q69 PNG (200 dpi rule, MAX_W=120).

if __name__ == '__main__':
    for q, path in FIG.items():
        img = Image.open(path)
        if img.mode == 'RGBA':
            bg = Image.new('RGBA', img.size, (255, 255, 255, 255))
            bg.alpha_composite(img)
            img = bg.convert('RGB')
        W, H = img.size
        print(f'== {q}  {path.name}  {W}x{H}px')
        rows = []
        for desc, box, kind in FEATURES[q]:
            px = measure(q, box, kind, img)
            rows.append((desc, px))
        head = '   ' + '特征'.ljust(26) + 'px'.rjust(7) + ''.join(f'{w:>9}mm' for w in WIDTHS[q])
        print(head)
        for desc, px in rows:
            line = '   ' + desc.ljust(26) + f'{px:7.1f}'
            for w in WIDTHS[q]:
                line += f'{px * w / W:10.2f} '
            print(line)
        print('   每毫米像素数: ' + '  '.join(f'{w}mm→{W / w:.1f}px/mm({W / w * 25.4:.0f}dpi)' for w in WIDTHS[q]))
