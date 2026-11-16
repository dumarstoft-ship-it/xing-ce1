"""Q46: read solid/dashed state of the 12 unit segments in each 2x2 grid.

Segment naming (2x2 grid, unit length 1):
  outer: T1 T2 (top, left->right), B1 B2 (bottom), L1 L2 (left, top->bottom), R1 R2 (right)
  inner: Vu Vd (middle vertical, upper/lower), Hl Hr (middle horizontal, left/right)
Coverage = fraction of sample points along the segment that are dark (max over a
small band across the line). Solid ~ 1.0, dashed ~ 0.5-0.7.
"""
from PIL import Image
import numpy as np

IMG = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s23_p12_i00.png'
im = np.array(Image.open(IMG).convert('L'))
dark = im < 140
H, W = im.shape


def find_grid(x0, x1, y0, y1):
    """Find left/center/right x and top/mid/bottom y of the inner grid inside a panel."""
    sub = dark[y0:y1, x0:x1]
    cs = sub.sum(axis=0)
    rs = sub.sum(axis=1)
    # candidate line positions: columns/rows with a lot of dark pixels
    cols = [x0 + i for i in range(len(cs)) if cs[i] > 0.35 * (y1 - y0) * 0.6]
    rows = [y0 + i for i in range(len(rs)) if rs[i] > 0.35 * (x1 - x0) * 0.6]
    return cols, rows


def cluster(v):
    out = []
    for x in v:
        if out and x - out[-1][-1] <= 2:
            out[-1].append(x)
        else:
            out.append([x])
    return [sum(c) / len(c) for c in out]


def coverage_h(y, xa, xb):
    ys = range(int(round(y)) - 1, int(round(y)) + 2)
    pts = range(int(xa) + 3, int(xb) - 2)
    hit = sum(1 for x in pts if any(dark[yy, x] for yy in ys))
    return hit / len(pts)


def coverage_v(x, ya, yb):
    xs = range(int(round(x)) - 1, int(round(x)) + 2)
    pts = range(int(ya) + 3, int(yb) - 2)
    hit = sum(1 for y in pts if any(dark[y, xx] for xx in xs))
    return hit / len(pts)


def analyse(x0, x1, y0, y1, label):
    cols, rows = find_grid(x0, x1, y0, y1)
    cx = cluster(cols)
    ry = cluster(rows)
    # keep the 3 inner lines (drop the panel frame if present)
    cx = [c for c in cx if x0 + 8 < c < x1 - 8]
    ry = [r for r in ry if y0 + 8 < r < y1 - 8]
    if len(cx) != 3 or len(ry) != 3:
        return label, None, cx, ry
    l, m, r = cx
    t, mid, b = ry
    seg = {
        'T1': coverage_h(t, l, m), 'T2': coverage_h(t, m, r),
        'B1': coverage_h(b, l, m), 'B2': coverage_h(b, m, r),
        'Hl': coverage_h(mid, l, m), 'Hr': coverage_h(mid, m, r),
        'L1': coverage_v(l, t, mid), 'L2': coverage_v(l, mid, b),
        'R1': coverage_v(r, t, mid), 'R2': coverage_v(r, mid, b),
        'Vu': coverage_v(m, t, mid), 'Vd': coverage_v(m, mid, b),
    }
    return label, seg, cx, ry


panels = [
    (7, 103, 7, 105, 'fig1'), (105, 200, 7, 105, 'fig2'), (202, 296, 7, 105, 'fig3'),
    (299, 394, 7, 105, 'fig4'), (397, 492, 7, 105, 'fig5'),
    (106, 201, 137, 235, 'A'), (203, 298, 137, 235, 'B'), (301, 396, 137, 235, 'C'),
    (399, 494, 137, 235, 'D'),
]
order = ['T1', 'T2', 'R1', 'R2', 'B2', 'B1', 'L2', 'L1', 'Vu', 'Vd', 'Hl', 'Hr']
results = {}
for p in panels:
    label, seg, cx, ry = analyse(*p)
    if seg is None:
        print(label, 'grid not found', cx, ry)
        continue
    s = ''.join('S' if seg[k] > 0.9 else 'd' for k in order)
    results[label] = {k: ('S' if seg[k] > 0.9 else 'd') for k in order}
    print(label, 'grid x', [round(c) for c in cx], 'y', [round(r) for r in ry])
    print('   ', ' '.join(f'{k}:{seg[k]:.2f}' for k in order))
    print('    pattern (T1 T2 R1 R2 B2 B1 L2 L1 | Vu Vd Hl Hr):', s[:8], s[8:])

print()
print('solid counts: outer / inner / total')
for k, v in results.items():
    outer = sum(v[x] == 'S' for x in order[:8])
    inner = sum(v[x] == 'S' for x in order[8:])
    print(k, outer, inner, outer + inner)

# ---- rule check: outer ring (8 unit edges, clockwise from top-left) shifts one edge
# clockwise per step; inner cross (4 arms) rotates 90 degrees counter-clockwise per step.
ring = order[:8]            # T1 T2 R1 R2 B2 B1 L2 L1  (clockwise)
arms = ['Vu', 'Hl', 'Vd', 'Hr']   # up, left, down, right  (counter-clockwise order)


def outer(lbl):
    return ''.join(results[lbl][k] for k in ring)


def inner(lbl):
    return ''.join(results[lbl][k] for k in arms)


figs = ['fig1', 'fig2', 'fig3', 'fig4', 'fig5']
ok_outer = all(outer(b) == outer(a)[-1] + outer(a)[:-1] for a, b in zip(figs, figs[1:]))
ok_inner = all(inner(b) == inner(a)[-1] + inner(a)[:-1] for a, b in zip(figs, figs[1:]))
print('\nouter ring shifts 1 edge clockwise each step:', ok_outer)
print('inner cross rotates 90 deg counter-clockwise each step:', ok_inner)
pred_outer = outer('fig5')[-1] + outer('fig5')[:-1]
pred_inner = inner('fig5')[-1] + inner('fig5')[:-1]
print('predicted 6th: outer', pred_outer, 'inner(up,left,down,right)', pred_inner)
for o in 'ABCD':
    print(o, 'outer', outer(o), 'inner', inner(o), '<- match' if (outer(o), inner(o)) == (pred_outer, pred_inner) else '')
