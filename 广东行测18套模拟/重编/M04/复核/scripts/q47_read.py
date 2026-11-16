"""Q47: read each 4x4 dot lattice (B = black circle, W = white circle, . = empty).

The lattice of each cell is located from the bounding box of the dark pixels inside the
cell (frame excluded); every position is classified from the centre pixel (dark -> B)
and from a ring of samples at ~0.4 pitch (dark ring with light centre -> W).
"""
import numpy as np
from PIL import Image

SRC = "/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s19_p12_i01.png"
im = np.array(Image.open(SRC).convert("L")).astype(int)

# frame lines found with a column/row darkness profile
GRID_X = [66, 155, 245, 334]
GRID_Y = [6, 94, 181, 268]
OPT_X = [8, 102, 200, 297, 393]
OPT_Y = [288, 383]


def find_opt_x():
    dark = im < 128
    cols = dark[OPT_Y[0] + 3:OPT_Y[1] - 3].sum(axis=0)
    return [i for i, c in enumerate(cols) if c > 80]


def read_cell(x0, y0, x1, y1):
    sub = im[y0 + 4:y1 - 3, x0 + 4:x1 - 3]
    dark = sub < 128
    ys, xs = np.nonzero(dark)
    bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
    pitch_x = (bx1 - bx0) / 4.0
    pitch_y = (by1 - by0) / 4.0
    grid = []
    for r in range(4):
        row = ""
        for c in range(4):
            cx = bx0 + pitch_x * (c + 0.5)
            cy = by0 + pitch_y * (r + 0.5)
            centre = sub[int(round(cy)), int(round(cx))]
            hits = []
            for ang in np.linspace(0, 2 * np.pi, 24, endpoint=False):
                hit = False
                for rad in np.linspace(0.30, 0.50, 6):
                    rx = cx + rad * pitch_x * np.cos(ang)
                    ry = cy + rad * pitch_y * np.sin(ang)
                    if sub[int(round(ry)), int(round(rx))] < 128:
                        hit = True
                hits.append(hit)
            ring_dark = np.mean(hits)
            if centre < 128:
                row += "B"
            elif ring_dark > 0.75:
                row += "W"
            else:
                row += "."
        grid.append(row)
    return grid, (bx1 - bx0, by1 - by0)


cells = {}
for r in range(3):
    for c in range(3):
        if (r, c) == (2, 2):
            continue
        g, size = read_cell(GRID_X[c], GRID_Y[r], GRID_X[c + 1], GRID_Y[r + 1])
        cells[f"R{r + 1}C{c + 1}"] = g
        print(f"R{r + 1}C{c + 1} bbox={size}")
        print("\n".join("   " + s for s in g))

print("option frame columns:", find_opt_x())
for i, name in enumerate("ABCD"):
    g, size = read_cell(OPT_X[i], OPT_Y[0], OPT_X[i + 1], OPT_Y[1])
    cells[name] = g
    print(f"{name} bbox={size}")
    print("\n".join("   " + s for s in g))
