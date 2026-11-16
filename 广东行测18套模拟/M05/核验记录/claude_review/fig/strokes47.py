# Q47: estimate odd-vertex count (=> stroke count) per cell from skeleton graph
import numpy as np
from PIL import Image
from collections import deque
im = np.array(Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s27_p12_i00.png').convert('L')).astype(int)
xs = [51, 150, 250, 350]; ys = [6, 100, 200, 300]
cells = {}
for r in range(3):
    for c in range(3):
        if (r, c) != (2, 2):
            cells['r%dc%d' % (r+1, c+1)] = (xs[c]+4, ys[r]+4, xs[c+1]-3, ys[r+1]-3)
bx = [6, 103, 200, 297, 394]
for i, L in enumerate('ABCD'):
    cells[L] = (bx[i]+4, 333, bx[i+1]-3, 425)
SCALE = 4
def zhang_suen(img):
    img = img.copy().astype(np.uint8)
    changed = True
    while changed:
        changed = False
        for step in (0, 1):
            P = np.pad(img, 1)
            p2 = P[:-2, 1:-1]; p3 = P[:-2, 2:]; p4 = P[1:-1, 2:]; p5 = P[2:, 2:]
            p6 = P[2:, 1:-1]; p7 = P[2:, :-2]; p8 = P[1:-1, :-2]; p9 = P[:-2, :-2]
            nb = [p2, p3, p4, p5, p6, p7, p8, p9]
            B = sum(n.astype(int) for n in nb)
            seq = nb + [p2]
            A = sum(((seq[k] == 0) & (seq[k+1] == 1)).astype(int) for k in range(8))
            if step == 0:
                c1 = (p2 * p4 * p6) == 0; c2 = (p4 * p6 * p8) == 0
            else:
                c1 = (p2 * p4 * p8) == 0; c2 = (p2 * p6 * p8) == 0
            m = (img == 1) & (B >= 2) & (B <= 6) & (A == 1) & c1 & c2
            if m.any():
                img[m] = 0; changed = True
    return img
def ring_count(mask, cy, cx, r):
    n = max(24, int(2 * np.pi * r * 2))
    vals = []
    for k in range(n):
        t = 2 * np.pi * k / n
        y = int(round(cy + r * np.sin(t))); x = int(round(cx + r * np.cos(t)))
        vals.append(1 if 0 <= y < mask.shape[0] and 0 <= x < mask.shape[1] and mask[y, x] else 0)
    # number of runs of 1s (circular)
    runs = sum(1 for k in range(n) if vals[k] == 1 and vals[k-1] == 0)
    if all(vals): runs = 1
    return runs
results = {}
for name, (x0, y0, x1, y1) in cells.items():
    sub = Image.fromarray(im[y0:y1, x0:x1].astype(np.uint8)).resize(((x1-x0)*SCALE, (y1-y0)*SCALE), Image.BICUBIC)
    a = np.array(sub).astype(int)
    mask = a < 140
    sk = zhang_suen(mask)
    P = np.pad(sk, 1)
    nbc = sum(np.roll(np.roll(P, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy, dx) != (0, 0))[1:-1, 1:-1] * sk
    cand = np.argwhere((sk == 1) & ((nbc == 1) | (nbc >= 3)))
    # cluster candidates
    clusters = []
    for (y, x) in cand:
        for cl in clusters:
            if abs(cl[0][0] - y) <= 4*SCALE and abs(cl[0][1] - x) <= 4*SCALE:
                cl.append((y, x)); break
        else:
            clusters.append([(y, x)])
    nodes = []
    for cl in clusters:
        cy = np.mean([p[0] for p in cl]); cx = np.mean([p[1] for p in cl])
        degs = [ring_count(mask, cy, cx, r) for r in (4*SCALE, 5*SCALE, 6*SCALE)]
        deg = max(set(degs), key=degs.count)
        nodes.append((cy / SCALE + y0, cx / SCALE + x0, deg, degs))
    odd = [n for n in nodes if n[2] % 2 == 1]
    results[name] = (len(odd), nodes)
    print('%-5s odd vertices: %d  -> strokes %d' % (name, len(odd), max(1, len(odd)//2)))
    for n in nodes:
        print('       node (x=%.1f, y=%.1f) deg=%d ring=%s' % (n[1], n[0], n[2], n[3]))
