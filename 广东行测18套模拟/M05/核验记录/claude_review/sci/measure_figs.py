# Read-only: measure print size of key details of Q66/67/70 figures in the source PDF.
# mm per px derived from 图片清单.json bbox_pt (1 pt = 25.4/72 mm).
import json
import numpy as np
from PIL import Image
ROOT = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/'
inv = {o['id']: o for o in json.load(open(ROOT + '图片清单.json'))}
PT = 25.4 / 72

def scale(aid):
    o = inv[aid]
    x0, y0, x1, y1 = o['bbox_pt']
    wmm, hmm = (x1 - x0) * PT, (y1 - y0) * PT
    return wmm, hmm, wmm / o['width_px'], hmm / o['height_px']

def dark(aid, thr=140):
    im = Image.open(ROOT + 'assets/' + aid + '.png').convert('L')
    return np.array(im) < thr

def bbox_dark(mask, box):
    x0, y0, x1, y1 = box
    sub = mask[y0:y1, x0:x1]
    ys, xs = np.nonzero(sub)
    if len(xs) == 0: return None
    return (x0 + xs.min(), y0 + ys.min(), x0 + xs.max(), y0 + ys.max())

def runs(arr):
    """lengths of consecutive True runs in a 1-D bool array -> list of (start, length)"""
    out, s = [], None
    for i, v in enumerate(arr):
        if v and s is None: s = i
        if not v and s is not None: out.append((s, i - s)); s = None
    if s is not None: out.append((s, len(arr) - s))
    return out

def report(aid, items, strokes, spacings):
    wmm, hmm, sx, sy = scale(aid)
    print(f'== {aid}: source print {wmm:.1f} x {hmm:.1f} mm; {sx:.4f} mm/px (x), {sy:.4f} mm/px (y); '
          f'= {25.4/sx:.0f} ppi effective')
    m = dark(aid)
    for name, box in items:
        bb = bbox_dark(m, box)
        if bb is None:
            print(f'   {name}: no ink in {box}'); continue
        w, h = bb[2] - bb[0] + 1, bb[3] - bb[1] + 1
        print(f'   {name:34s} ink bbox {bb}: {w}x{h}px -> {w*sx:.2f} x {h*sy:.2f} mm')
    for name, (axis, pos, rng) in strokes:
        if axis == 'col':
            line = m[rng[0]:rng[1], pos]
            rr = runs(line)
            print(f'   {name:34s} column x={pos}, y{rng}: runs(px)={[(r[0]+rng[0], r[1]) for r in rr]}')
        else:
            line = m[pos, rng[0]:rng[1]]
            rr = runs(line)
            print(f'   {name:34s} row y={pos}, x{rng}: runs(px)={[(r[0]+rng[0], r[1]) for r in rr]}')
    for name, px, axis in spacings:
        s = sx if axis == 'x' else sy
        print(f'   {name:34s} {px}px -> {px*s:.2f} mm')
    return sx, sy

# ---------- Q66 ----------
sx66, sy66 = report('s32_p17_i01', [
    ('label 2f静max (whole)',            (300, 25, 372, 50)),
    ('label f静max (whole)',             (300, 65, 372, 92)),
    ('axis label F',                     (368, 0, 395, 30)),
    ('axis label t (x-axis end)',        (585, 105, 600, 135)),
    ('origin O',                         (350, 120, 372, 150)),
    ('tick label t1 (with subscript)',   (390, 128, 412, 161)),
    ('tick label t2 (with subscript)',   (418, 128, 440, 161)),
    ('tick label t3 (with subscript)',   (458, 128, 482, 161)),
    ('arrow label F (box sketch)',       (140, 70, 170, 100)),
], [
    ('stroke: curve/axis (vertical axis)', ('row', 80, (360, 380))),
    ('dashes on f level (y~82)',           ('row', 82, (378, 475))),
    ('dashes at t2 (x~425)',               ('col', 425, (40, 130))),
], [
    ('t1->t2 tick spacing (~401->425)', 24, 'x'),
    ('t2->t3 tick spacing (~425->470)', 45, 'x'),
    ('f level -> 2f level vertical',    46, 'y'),
])

# ---------- Q67 ----------
sx67, sy67 = report('s27_p18_i01', [
    ('label R',                          (235, 85, 270, 120)),
    ('label R0 (with subscript)',        (520, 285, 574, 325)),
    ('label L1 (with subscript)',        (225, 285, 275, 325)),
    ('label L2 (with subscript)',        (345, 550, 400, 599)),
    ('ammeter A1 circle',                (85, 350, 160, 420)),
    ('ammeter A2 circle',                (130, 485, 205, 555)),
    ('label S',                          (355, 395, 385, 435)),
    ('lamp L1 circle',                   (205, 195, 285, 270)),
    ('slider arrowhead',                 (240, 35, 270, 55)),
], [
    ('top wire stroke (col x=100)',        ('col', 100, (50, 75))),
    ('slider wire top (col x=320)',        ('col', 320, (0, 20))),
    ('switch gap (row y=385)',             ('row', 385, (330, 420))),
], [
    ('R right end -> slider-wire drop (295->385)', 90, 'x'),
    ('slider wire height above R body (8->52)',     44, 'y'),
])

# ---------- Q70 ----------
sx70, sy70 = report('s23_p19_i11', [
    ('contour label 1320 (peak)',        (163, 120, 220, 145)),
    ('contour label 1000 (甲山)',          (380, 172, 440, 200)),
    ('contour label 800',                (410, 197, 460, 222)),
    ('contour label 200',                (560, 290, 610, 318)),
    ('contour label 0',                  (585, 328, 605, 352)),
    ('point label A',                    (250, 130, 272, 157)),
    ('point label B',                    (265, 40, 290, 65)),
    ('point label C',                    (560, 130, 585, 158)),
    ('point label D',                    (465, 118, 490, 145)),
    ('point label E',                    (240, 202, 262, 228)),
    ('point label G',                    (30, 150, 55, 178)),
    ('point label H',                    (430, 258, 455, 285)),
    ('char 甲山',                          (310, 140, 365, 168)),
    ('char 丙',                            (210, 372, 240, 400)),
    ('scale text 1:300000',              (10, 410, 125, 445)),
    ('north arrow (whole)',              (555, 20, 615, 75)),
    ('B point dot',                      (288, 44, 300, 56)),
    ('peak triangle 1320',               (140, 120, 165, 145)),
], [
    ('contour stroke (col x=100 top)',     ('col', 100, (0, 140))),
    ('contours at B column (x=292)',       ('col', 292, (0, 130))),
    ('contours along CD row (y=158)',      ('row', 158, (460, 643))),
    ('cliff ticks (col x=62, y 90-250)',   ('col', 62, (85, 250))),
    ('EF dashes (col x=290..)',            ('col', 290, (200, 240))),
], [
    ('U-line bottom (y~40) -> 600 line at B (y~70)', 30, 'y'),
    ('ridge bulge depth at CD (approx)', 40, 'x'),
])
