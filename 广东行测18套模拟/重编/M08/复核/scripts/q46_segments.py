"""第46题：读取每个小图12段线（外框8段+内部十字4段）的实/虚状态。
对每段沿线采样，统计暗像素比例：实线≈1.0，虚线≈0.5-0.7。"""
from PIL import Image
import numpy as np

IMG = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s23_p12_i00.png'
im = np.array(Image.open(IMG).convert('L'))
dark = im < 140

def find_lines(arr1d, thr):
    xs = [i for i, v in enumerate(arr1d) if v > thr]
    groups = []
    for x in xs:
        if groups and x - groups[-1][-1] <= 1:
            groups[-1].append(x)
        else:
            groups.append([x])
    return [int(round(sum(g) / len(g))) for g in groups]

def analyze(x0, x1, y0, y1):
    sub = dark[y0:y1, x0:x1]
    # inner square columns/rows: lines with >= 25 dark pixels
    cols = find_lines(sub.sum(axis=0), 25)
    rows = find_lines(sub.sum(axis=1), 25)
    return cols, rows

def frac(p, q, axis):
    # fraction of dark pixels along a segment from p to q (exclusive of endpoints margin)
    (xa, ya), (xb, yb) = p, q
    vals = []
    if axis == 'h':
        y = ya
        for x in range(min(xa, xb) + 3, max(xa, xb) - 2):
            vals.append(dark[y - 1:y + 2, x].any())
    else:
        x = xa
        for y in range(min(ya, yb) + 3, max(ya, yb) - 2):
            vals.append(dark[y, x - 1:x + 2].any())
    return sum(vals) / len(vals)

def panel_state(x0, x1, y0, y1):
    cols, rows = analyze(x0, x1, y0, y1)
    # remove frame lines (close to panel border)
    cols = [c for c in cols if 5 < c < (x1 - x0) - 5]
    rows = [r for r in rows if 5 < r < (y1 - y0) - 5]
    assert len(cols) == 3 and len(rows) == 3, (cols, rows)
    xl, xm, xr = [x0 + c for c in cols]
    yt, ym, yb = [y0 + r for r in rows]
    segs = {
        'T1': ((xl, yt), (xm, yt), 'h'), 'T2': ((xm, yt), (xr, yt), 'h'),
        'R1': ((xr, yt), (xr, ym), 'v'), 'R2': ((xr, ym), (xr, yb), 'v'),
        'B2': ((xm, yb), (xr, yb), 'h'), 'B1': ((xl, yb), (xm, yb), 'h'),
        'L2': ((xl, ym), (xl, yb), 'v'), 'L1': ((xl, yt), (xl, ym), 'v'),
        'U': ((xm, yt), (xm, ym), 'v'), 'D': ((xm, ym), (xm, yb), 'v'),
        'Lh': ((xl, ym), (xm, ym), 'h'), 'Rh': ((xm, ym), (xr, ym), 'h'),
    }
    out = {}
    for k, (p, q, a) in segs.items():
        f = frac(p, q, a)
        out[k] = 'S' if f > 0.9 else 'd'
    return out, (xl, xm, xr, yt, ym, yb)

ORDER = ['T1', 'T2', 'R1', 'R2', 'B2', 'B1', 'L2', 'L1', 'U', 'Rh', 'D', 'Lh']
top = [(6, 103), (104, 200), (201, 297), (298, 395), (396, 493)]
opts = [(105, 201), (202, 299), (300, 397), (398, 494)]
panels = {}
for i, (a, b) in enumerate(top):
    st, geo = panel_state(a, b, 6, 106)
    panels[f'F{i+1}'] = st
for i, (a, b) in enumerate(opts):
    st, geo = panel_state(a, b, 135, 236)
    panels['ABCD'[i]] = st

print('order (clockwise outer from top-left half, then inner U,Rh,D,Lh):', ORDER)
for name, st in panels.items():
    s = ''.join(st[k] for k in ORDER)
    outer = ''.join(st[k] for k in ORDER[:8])
    inner = ''.join(st[k] for k in ORDER[8:])
    nS = sum(1 for k in ORDER if st[k] == 'S')
    print(f'{name}: outer={outer} inner={inner}  solid_total={nS} outer_solid={outer.count("S")} inner_solid={inner.count("S")}')
