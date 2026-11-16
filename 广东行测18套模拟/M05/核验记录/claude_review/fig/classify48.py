# Q48: classify each glyph into half-segments on a 3x3 lattice (rows top/mid/bot, cols left/center/right)
import numpy as np
from PIL import Image
im = np.array(Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s31_p12_i00.png').convert('L'))
dark = im < 128
def colsegs(a, b, x0, x1):
    cols = dark[a:b+1, x0:x1].sum(0); seg = []; inb = False
    for x in range(len(cols)):
        if cols[x] > 0 and not inb: s = x; inb = True
        if cols[x] == 0 and inb: seg.append((s+x0, x-1+x0)); inb = False
    if inb: seg.append((s+x0, x1-1))
    return seg
rows = {'box': (27, 61), 'A': (106, 140), 'B': (163, 197), 'C': (221, 255), 'D': (278, 312)}
xr = {'box': (41, 491), 'A': (50, 500), 'B': (50, 500), 'C': (50, 500), 'D': (50, 500)}
def band_frac(y0, y1, x0, x1):
    return dark[y0:y1+1, x0:x1+1].mean()
names = {}
def classify(a, b, x0, x1):
    # glyph extents
    sub = dark[a:b+1, x0:x1+1]
    yy, xx = np.nonzero(sub)
    gy0, gy1, gx0, gx1 = a + yy.min(), a + yy.max(), x0 + xx.min(), x0 + xx.max()
    Y = {'t': (gy0, gy0+1), 'm': None, 'b': (gy1-1, gy1)}
    X = {'l': (gx0, gx0+1), 'c': None, 'r': (gx1-1, gx1)}
    # find middle lines: rows/cols with long dark runs inside
    ym = (gy0 + gy1) / 2; xm = (gx0 + gx1) / 2
    Y['m'] = (int(round(ym)) - 1, int(round(ym)) + 1)
    X['c'] = (int(round(xm)) - 1, int(round(xm)) + 1)
    segs = []
    margin = 4
    # horizontal half segments: row r in t,m,b ; half L (gx0..xm) R (xm..gx1)
    for rn, (ya, yb) in Y.items():
        fl = dark[ya:yb+1, gx0+margin:int(xm)-margin].any(0).mean()
        fr = dark[ya:yb+1, int(xm)+margin:gx1-margin+1].any(0).mean()
        if fl > 0.8: segs.append('H%s-L' % rn)
        if fr > 0.8: segs.append('H%s-R' % rn)
    for cn, (xa, xb) in X.items():
        fu = dark[gy0+margin:int(ym)-margin, xa:xb+1].any(1).mean()
        fd = dark[int(ym)+margin:gy1-margin+1, xa:xb+1].any(1).mean()
        if fu > 0.8: segs.append('V%s-U' % cn)
        if fd > 0.8: segs.append('V%s-D' % cn)
    # total dark-pixel check vs reconstruction
    return segs, (gx0, gx1, gy0, gy1)
def pretty(segs):
    # 5x5 char drawing
    g = [[' ']*5 for _ in range(5)]
    ry = {'t': 0, 'm': 2, 'b': 4}; cx = {'l': 0, 'c': 2, 'r': 4}
    for s in segs:
        if s[0] == 'H':
            y = ry[s[1]]
            xs = range(0, 3) if s.endswith('L') else range(2, 5)
            for x in xs: g[y][x] = '-' if g[y][x] == ' ' else '+'
        else:
            x = cx[s[1]]
            ys = range(0, 3) if s.endswith('U') else range(2, 5)
            for y in ys: g[y][x] = '|' if g[y][x] == ' ' else '+'
    return [''.join(r) for r in g]
allres = {}
for k, (a, b) in rows.items():
    segs = colsegs(a, b, *xr[k])
    if k != 'box': segs = [s for s in segs if s[0] > 50]
    res = []
    for (x0, x1) in segs:
        s, ext = classify(a, b, x0, x1)
        res.append(s)
    allres[k] = res
    print('=====', k, len(res), 'glyphs')
    pics = [pretty(s) for s in res]
    for line in range(5):
        print('   ' + '   '.join(p[line] for p in pics))
    for i, s in enumerate(res):
        print('   #%d' % (i+1), ' '.join(s))
import json
json.dump(allres, open('q48_glyphs.json', 'w'), ensure_ascii=False, indent=1)
