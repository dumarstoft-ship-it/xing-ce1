"""rmat.py <tag> <q0> <q1> <out.png> [dpi] [mode]
mode 'm' (default): material region = from end of question q0-1 to start of question q0 (stitched across pages).
mode 'mq': material + questions q0..q1.
mode 'q': questions only.
Uses the faithful renderer (masks page furniture only)."""
import json, sys, os
sys.path.insert(0, '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl2a/bin')
from render2 import render_material
import pymupdf
W = '/home/user/work'
tag, q0, q1, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
dpi = int(sys.argv[5]) if len(sys.argv) > 5 else 150
mode = sys.argv[6] if len(sys.argv) > 6 else 'm'
d = json.load(open(f'{W}/index/{tag}.json'))
qs = {x['qno']: x for x in d if x['kind'] == 'q'}
f = qs[q0]['file']
doc = pymupdf.open('/home/user/' + f)
prev = qs.get(q0 - 1)
if prev and prev['segs'][-1][0] <= qs[q0]['segs'][0][0]:
    ps, ys = prev['segs'][-1][0], prev['segs'][-1][2]
else:
    ps, ys = qs[q0]['segs'][0][0], 0
if mode == 'q':
    ps, ys = qs[q0]['segs'][0][0], qs[q0]['segs'][0][1]
if mode in ('mq', 'q'):
    pe, ye = qs[q1]['segs'][-1][0], qs[q1]['segs'][-1][2]
else:
    pe, ye = qs[q0]['segs'][0][0], qs[q0]['segs'][0][1]
segs = []
for p in range(ps, pe + 1):
    y0 = ys if p == ps else 0
    y1 = ye if p == pe else doc[p].rect.height
    if y1 - y0 > 5: segs.append([p, y0, y1])
im, _ = render_material(f, segs, dpi=dpi)
im.save(out)
print(out, im.size, 'segs', [[s[0], round(s[1], 1), round(s[2], 1)] for s in segs])
