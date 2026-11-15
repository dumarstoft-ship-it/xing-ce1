#!/usr/bin/env python3
"""第35题重建图逐格可读性测量：每个数字字形到竖直/水平直径和圆周的最小像素距离。
只读仓库 PNG/SVG；输出 q35_legibility.json 与 q35_print_preview.png（按 150mm 宽、300dpi 模拟打印缩放）。"""
import json, math, re, sys
from pathlib import Path
from PIL import Image
import numpy as np
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/home/user/xing-ce1')
D = ROOT/'广东行测18套模拟/M03/编辑底稿'
OUT = Path(__file__).resolve().parent
svg = (D/'quant_data_number_grid.svg').read_text(encoding='utf-8')
im = Image.open(D/'quant_data_number_grid.png').convert('L')
a = np.array(im) < 128
sc = im.width/720
centers = [(float(x), float(y)) for x, y in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)"', svg)]
r = 70
texts = [(float(x), float(y), t) for x, y, t in re.findall(r'<text x="([\d.]+)" y="([\d.]+)"[^>]*>([^<]+)</text>', svg)]
lw = 1.8*sc
res = []
for ci, (cx, cy) in enumerate(centers):
    X, Y = cx*sc, cy*sc; R = r*sc
    for tx, ty, t in texts:
        if abs(tx-cx) > 70 or abs(ty-cy) > 70: continue
        quad = ('上' if ty < cy else '下') + ('左' if tx < cx else '右')
        # quadrant box (inside lines)
        x0 = X if tx > cx else X-R; x1 = X+R if tx > cx else X
        y0 = Y if ty > cy else Y-R; y1 = Y+R if ty > cy else Y
        ys, xs = np.nonzero(a[int(y0):int(y1), int(x0):int(x1)])
        ys = ys+int(y0); xs = xs+int(x0)
        # glyph pixels: not on vertical line, horizontal line or the circle
        dv = np.abs(xs-X); dh = np.abs(ys-Y); dc = np.abs(np.hypot(xs-X, ys-Y)-R)
        glyph = (dv > lw) & (dh > lw) & (dc > lw)
        gx, gy = xs[glyph], ys[glyph]
        if len(gx) == 0: continue
        to_v = float(np.min(np.abs(gx-X)) - lw/2)
        to_h = float(np.min(np.abs(gy-Y)) - lw/2)
        to_c = float(np.min(R - np.hypot(gx-X, gy-Y)) - lw/2)
        res.append({'circle': ci+1, 'quadrant': quad, 'text': t,
                    'gap_to_vertical_px': round(to_v, 1), 'gap_to_horizontal_px': round(to_h, 1),
                    'gap_to_circle_px': round(to_c, 1),
                    'gap_to_vertical_mm_at_150mm_width': round(to_v/(im.width/150), 2)})
for x in res:
    print(x)
json.dump({'png_size': im.size, 'stroke_px': lw, 'cells': res}, open(OUT/'q35_legibility.json', 'w'), ensure_ascii=False, indent=1)
# 模拟打印：图宽150mm、300dpi
w = round(150/25.4*300); h = round(w*im.height/im.width)
im.resize((w, h), Image.LANCZOS).save(OUT/'q35_print_preview.png')
print('preview', w, h, 'stroke mm', round(lw/(im.width/150), 2))
