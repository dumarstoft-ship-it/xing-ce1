"""Q35 print-size legibility check.
Simulate 120 mm figure width on A4 at 300 dpi (1417 px wide) and measure, with
8-connected components, whether each glyph (esp. the minus signs of -4 / -15)
is separate from the divider/circle strokes, and the minimum white gap in mm."""
import sys, json
from collections import deque
import numpy as np
from PIL import Image

SRC = '/home/user/xing-ce1/广东行测18套模拟/M03/assets/q35_number_grid_v020.png'
# 用法：python3 q35_print_check.py [输出目录]；缺省输出到脚本旁的 q35_check/
import os
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'q35_check')
os.makedirs(OUT, exist_ok=True)
im = Image.open(SRC).convert('L')
W0, H0 = im.size
PRINT_W_MM = 120.0
DPI = 300
Wp = round(PRINT_W_MM / 25.4 * DPI)
Hp = round(H0 * Wp / W0)

def components(mask):
    h, w = mask.shape
    lab = np.zeros((h, w), np.int32)
    comps = []
    ys, xs = np.nonzero(mask)
    cur = 0
    for y0, x0 in zip(ys, xs):
        if lab[y0, x0]:
            continue
        cur += 1
        q = deque([(y0, x0)]); lab[y0, x0] = cur; pts = []
        while q:
            y, x = q.popleft(); pts.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y+dy, x+dx
                    if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not lab[yy, xx]:
                        lab[yy, xx] = cur; q.append((yy, xx))
        comps.append(np.array(pts))
    return lab, comps

# text anchors in logical 720x180 coords (from SVG)
texts = []
for ci, (cx, vals) in enumerate([(90, ['25','3','7','−4']), (270, ['14','8','6','34']),
                                 (450, ['51','9','4','−15']), (630, ['22','8','7','?'])]):
    for (dx, dy), v in zip([(-32,-22),(32,-22),(-32,22),(32,22)], vals):
        texts.append({'circle': ci+1, 'text': v, 'x': cx+dx, 'y': 90+dy, 'cx': cx})

results = {}
for name, img, mm_per_px in [
        ('native_2160', im, PRINT_W_MM / W0),
        ('print_1417_lanczos', im.resize((Wp, Hp), Image.LANCZOS), 25.4/DPI),
        ('print_1417_box', im.resize((Wp, Hp), Image.BOX), 25.4/DPI)]:
    a = np.asarray(img).astype(np.int32)
    sx = img.size[0] / 720.0
    res_v = {}
    for thr in (128, 200, 240):
        mask = a < thr
        lab, comps = components(mask)
        sizes = [len(c) for c in comps]
        # line components: those whose bbox width > 100 logical units*scale*0.9 (circle+dividers)
        line_ids = [i for i, c in enumerate(comps)
                    if (c[:,1].max()-c[:,1].min()) > 120*sx]
        line_pts = np.concatenate([comps[i] for i in line_ids]) if line_ids else np.zeros((0,2))
        rows = []
        for t in texts:
            # glyph comps whose centroid is within the text cell (+-26 logical x, +-16 logical y)
            tx, ty = t['x']*sx, t['y']*sx
            gids = []
            for i, c in enumerate(comps):
                if i in line_ids: continue
                my, mx = c[:,0].mean(), c[:,1].mean()
                if abs(mx-tx) < 30*sx and abs(my-ty) < 18*sx:
                    gids.append(i)
            glyphs = []
            for i in sorted(gids, key=lambda i: comps[i][:,1].min()):
                c = comps[i]
                # nearest line pixel
                y0,y1,x0,x1 = c[:,0].min(), c[:,0].max(), c[:,1].min(), c[:,1].max()
                near = line_pts[(line_pts[:,0] > y0-60) & (line_pts[:,0] < y1+60) &
                                (line_pts[:,1] > x0-60) & (line_pts[:,1] < x1+60)]
                if len(near):
                    d = np.sqrt(((c[:,None,:]-near[None,:,:])**2).sum(-1)).min()
                    # gap = centre distance minus 1 px (pixel to pixel edge)
                    gap_px = max(d-1, 0)
                else:
                    gap_px = None
                # horizontal gap from vertical divider right edge in same rows
                vx = t['cx']*sx
                div = line_pts[(np.abs(line_pts[:,1]-vx) < 3*sx) & (line_pts[:,0] >= y0) & (line_pts[:,0] <= y1)]
                hgap = (x0 - div[:,1].max() - 1) if (len(div) and x0 > vx) else None
                glyphs.append({'bbox_px': [int(x0),int(y0),int(x1),int(y1)], 'w_px': int(x1-x0+1), 'h_px': int(y1-y0+1),
                               'pixels': int(len(c)),
                               'min_gap_to_line_px': None if gap_px is None else round(float(gap_px),2),
                               'min_gap_to_line_mm': None if gap_px is None else round(float(gap_px)*mm_per_px,3),
                               'h_gap_to_vertical_divider_mm': None if hgap is None else round(float(hgap)*mm_per_px,3)})
            rows.append({'circle': t['circle'], 'text': t['text'], 'n_components': len(glyphs), 'glyphs': glyphs})
        res_v[f'thr{thr}'] = {'n_line_components': len(line_ids), 'cells': rows}
    results[name] = {'size': list(img.size), 'mm_per_px': round(mm_per_px,5), 'by_threshold': res_v}
    if name.startswith('print'):
        img.save(f'{OUT}/q35_{name}.png', dpi=(DPI,DPI))
        # zoomed crops of the two negative cells (x8 nearest)
        for lbl, cx in (('m4', 90), ('m15', 450)):
            box = (int((cx-8)*sx), int(92*sx), int((cx+70)*sx), int(140*sx))
            img.crop(box).resize(((box[2]-box[0])*8, (box[3]-box[1])*8), Image.NEAREST).save(f'{OUT}/q35_{name}_{lbl}_x8.png')

json.dump(results, open(f'{OUT}/q35_print_check.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
# compact summary
for name, r in results.items():
    print('==', name, r['size'], 'mm/px', r['mm_per_px'])
    for thr, rv in r['by_threshold'].items():
        print('  ', thr, 'line comps', rv['n_line_components'])
        for row in rv['cells']:
            g = row['glyphs']
            mins = [x['min_gap_to_line_mm'] for x in g if x['min_gap_to_line_mm'] is not None]
            hg = [x['h_gap_to_vertical_divider_mm'] for x in g if x['h_gap_to_vertical_divider_mm'] is not None]
            print(f"     c{row['circle']} {row['text']:>4} comps={row['n_components']} min_gap_mm={min(mins) if mins else None} first_glyph={g[0]['bbox_px'] if g else None} w={g[0]['w_px'] if g else None} h={g[0]['h_px'] if g else None} hgap_div_mm={hg[0] if hg else None}")
