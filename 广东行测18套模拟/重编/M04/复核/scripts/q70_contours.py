"""Q70: separate the solid contour lines (large connected components) from dashes
(ski runs) and text, render each contour component in its own colour, and list the
components crossed along transects.  Usage: python3 q70_contours.py <out_dir>"""
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageDraw

SRC = "/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s19_p19_i00.png"
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
im = np.array(Image.open(SRC).convert("L"))
H, W = im.shape
dark = im < 150
# erase the outer frame and the legend box (and its content) so that contour lines
# touching the frame are not merged into one component
dark[:6, :] = False
dark[384:, :] = False
dark[:, :6] = False
dark[:, 593:] = False
dark[249:, :196] = False
# erase the circled run labels (1) and (2); they touch neighbouring contours and would
# merge two different contour lines into one component
yy, xx = np.mgrid[0:H, 0:W]
for cx, cy, r in ((277.5, 130.5, 16.5), (379.0, 120.0, 16.0)):
    dark[(xx - cx) ** 2 + (yy - cy) ** 2 <= r ** 2] = False


def label(mask):
    lab = np.zeros(mask.shape, int)
    n = 0
    sizes = {}
    for y in range(mask.shape[0]):
        for x in range(mask.shape[1]):
            if mask[y, x] and not lab[y, x]:
                n += 1
                q = deque([(y, x)])
                lab[y, x] = n
                cnt = 0
                while q:
                    cy, cx = q.popleft()
                    cnt += 1
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1] and mask[ny, nx] and not lab[ny, nx]:
                                lab[ny, nx] = n
                                q.append((ny, nx))
                sizes[n] = cnt
    return lab, sizes


lab, sizes = label(dark)
big = {k: v for k, v in sizes.items() if v >= 120}
print("components >=120 px:", len(big))
rng = np.random.default_rng(3)
colors = {k: tuple(int(c) for c in rng.integers(30, 230, 3)) for k in big}
rgb = np.full((H, W, 3), 255, np.uint8)
small = (lab > 0) & ~np.isin(lab, list(big))
rgb[small] = (170, 170, 170)
for k in big:
    rgb[lab == k] = colors[k]
img = Image.fromarray(rgb).resize((W * 3, H * 3), Image.NEAREST)
d = ImageDraw.Draw(img)
for k in big:
    ys, xs = np.nonzero(lab == k)
    i = len(ys) // 2
    order = np.argsort(xs)
    yy, xx = ys[order][i], xs[order][i]
    d.text((xx * 3 + 4, yy * 3 - 12), str(k), fill=(0, 0, 0))
img.save(f"{OUT}/q70_components.png")
np.save(f"{OUT}/q70_labels.npy", lab)
for k, v in sorted(big.items(), key=lambda kv: -kv[1]):
    ys, xs = np.nonzero(lab == k)
    print(f"comp {k:4d} size {v:5d} bbox x[{xs.min()},{xs.max()}] y[{ys.min()},{ys.max()}]")
