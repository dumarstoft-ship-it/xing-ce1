"""Q47: count enclosed light regions (closed spaces) per cell straight from pixels, at
several thresholds; report how many are big (white-circle interiors / enclosed empty
lattice positions) and how many are tiny (the star-shaped gaps between 2x2 circles)."""
from collections import deque

import numpy as np
from PIL import Image

SRC = "/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s19_p12_i01.png"
im = np.array(Image.open(SRC).convert("L")).astype(int)
GRID_X = [66, 155, 245, 334]
GRID_Y = [6, 94, 181, 268]
OPT_X = [5, 102, 200, 297, 394]
OPT_Y = [288, 383]

boxes = {}
for r in range(3):
    for c in range(3):
        if (r, c) != (2, 2):
            boxes[f"R{r + 1}C{c + 1}"] = (GRID_X[c] + 3, GRID_Y[r] + 3, GRID_X[c + 1] - 2, GRID_Y[r + 1] - 2)
for i, n in enumerate("ABCD"):
    boxes[n] = (OPT_X[i] + 3, OPT_Y[0] + 3, OPT_X[i + 1] - 2, OPT_Y[1] - 2)


def regions(light):
    h, w = light.shape
    seen = np.zeros_like(light, dtype=bool)
    out = []
    for y in range(h):
        for x in range(w):
            if light[y, x] and not seen[y, x]:
                q = deque([(y, x)])
                seen[y, x] = True
                n, border = 0, False
                while q:
                    cy, cx = q.popleft()
                    n += 1
                    if cy in (0, h - 1) or cx in (0, w - 1):
                        border = True
                    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and light[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            q.append((ny, nx))
                if not border:
                    out.append(n)
    return out


for thr in (128, 170, 210):
    print(f"--- light threshold {thr}")
    for k, (x0, y0, x1, y1) in boxes.items():
        sub = im[y0:y1, x0:x1]
        regs = regions(sub >= thr)
        big = [n for n in regs if n >= 20]
        tiny = [n for n in regs if n < 20]
        print(f"{k:5} closed={len(regs):2} big={len(big):2} tiny={len(tiny):2} tiny_sizes={sorted(tiny)}")
