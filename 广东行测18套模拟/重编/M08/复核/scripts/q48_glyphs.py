"""第48题：切出框内与各选项的8个圆柱图元，按像素相似度判定哪些图元完全相同，
并给出每个图元的朝向（看得见的那个底面椭圆在哪一侧）。"""
from PIL import Image, ImageDraw
import numpy as np
from scipy import ndimage
import sys

IMG = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s23_p12_i02.png'
OUT = sys.argv[1] if len(sys.argv) > 1 else None
im = Image.open(IMG).convert('L')
a = np.array(im) < 150
lab, n = ndimage.label(a)
objs = ndimage.find_objects(lab)
items = []
for i, sl in enumerate(objs):
    ys, xs = sl
    h = ys.stop - ys.start; w = xs.stop - xs.start
    if 15 < h < 60 and 15 < w < 60:
        cy = (ys.start + ys.stop) / 2; cx = (xs.start + xs.stop) / 2
        items.append((cy, cx, sl, i + 1))
rows = {'frame': (0, 60), 'A': (60, 125), 'B': (125, 180), 'C': (180, 240), 'D': (240, 295)}
groups = {}
for k, (y0, y1) in rows.items():
    g = [it for it in items if y0 <= it[0] < y1]
    g.sort(key=lambda t: t[1])
    groups[k] = g
    assert len(g) == 8, (k, len(g))

def glyph(it, size=48):
    cy, cx, sl, idx = it
    ys, xs = sl
    m = (lab[sl] == idx).astype(np.uint8) * 255
    canvas = np.zeros((size, size), np.uint8)
    h, w = m.shape
    oy = (size - h) // 2; ox = (size - w) // 2
    canvas[oy:oy + h, ox:ox + w] = m
    return canvas

G = {k: [glyph(it) for it in v] for k, v in groups.items()}
allg = [(k, i, g) for k, v in G.items() for i, g in enumerate(v)]

def sim(g1, g2):
    # best IoU over small shifts
    best = 0
    A = g1 > 0
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            B = np.roll(np.roll(g2 > 0, dy, 0), dx, 1)
            # dilate both a bit for tolerance
            Ad = ndimage.binary_dilation(A, iterations=1)
            Bd = ndimage.binary_dilation(B, iterations=1)
            inter = (Ad & Bd).sum(); uni = (Ad | Bd).sum()
            best = max(best, inter / uni)
    return best

# cluster glyphs into types by similarity threshold
types = []
labels = {}
for k, i, g in allg:
    for t_idx, rep in enumerate(types):
        if sim(g, rep) > 0.85:
            labels[(k, i)] = t_idx
            break
    else:
        types.append(g)
        labels[(k, i)] = len(types) - 1

for k in groups:
    print(k, [labels[(k, i)] for i in range(8)])

if OUT:
    # contact sheet of types
    sheet = Image.new('L', (len(types) * 60, 70), 255)
    d = ImageDraw.Draw(sheet)
    for t_idx, g in enumerate(types):
        sheet.paste(Image.fromarray(255 - g), (t_idx * 60 + 6, 2))
        d.text((t_idx * 60 + 25, 55), str(t_idx), fill=0)
    sheet = sheet.resize((sheet.size[0] * 4, sheet.size[1] * 4), Image.NEAREST)
    sheet.save(OUT)
