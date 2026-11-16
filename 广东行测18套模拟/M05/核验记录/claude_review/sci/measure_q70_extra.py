# Read-only: Q70 cliff tick spacing (scan parallel to the cliff line) and B-dot clearance.
import json
import numpy as np
from PIL import Image
ROOT = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/'
inv = {o['id']: o for o in json.load(open(ROOT + '图片清单.json'))}
PT = 25.4 / 72
o = inv['s23_p19_i11']
x0, y0, x1, y1 = o['bbox_pt']; s = (x1 - x0) * PT / o['width_px']
m = np.array(Image.open(ROOT + 'assets/s23_p19_i11.png').convert('L')) < 150
# locate cliff line: for each y in 90..245, darkest long-run x near expected position
pts = []
for y in range(92, 246, 1):
    xs = [x for x in range(50, 95) if m[y, x]]
    if xs: pts.append((y, xs))
# scan 5 px left of the cliff main line (approx line from (57,90) to (85,247))
hits = []
for y in range(90, 248):
    xc = 57 + (85 - 57) * (y - 90) / (247 - 90)
    xs = int(round(xc - 6))
    hits.append(1 if m[y, xs] else 0)
runs, st = [], None
for i, v in enumerate(hits):
    if v and st is None: st = i
    if not v and st is not None: runs.append((90 + st, i - st)); st = None
centers = [r[0] + r[1] / 2 for r in runs]
gaps = [round(b - a, 1) for a, b in zip(centers, centers[1:])]
print('cliff tick crossings (y,len):', runs)
print('tick pitch px:', gaps, '-> mean %.1f px = %.2f mm' % (np.mean(gaps), np.mean(gaps) * s))
# tick length: horizontal run left of the cliff line at a tick row
for (yy, ln) in runs[:4]:
    yc = int(yy + ln // 2)
    row = m[yc, 30:100]
    xs = np.nonzero(row)[0] + 30
    print(f'  tick row y={yc}: dark x from {xs.min()} to {xs.max()} -> extent {(xs.max()-xs.min()+1)*s:.2f} mm (incl. main line)')
# B dot clearance along column x=295
col = m[0:110, 295]
r, st = [], None
for i, v in enumerate(col):
    if v and st is None: st = i
    if not v and st is not None: r.append((st, i - st)); st = None
print('column x=295 dark runs (y,len):', r)
print('mm per px:', round(s, 4))
