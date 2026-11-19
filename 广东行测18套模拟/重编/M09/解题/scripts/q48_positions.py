# -*- coding: utf-8 -*-
"""M09 第48题（GD2020-XZ-Q046）：九宫格里两个小图形所在的格子。

同一种外框（圆、三角形、正方形）在各图里是同一幅画，只是小图形不同。把同种外框的各图按外框
外接矩形对齐，取“每幅都是黑的”像素作为外框连同格线的公共底图，各图减去（加粗后的）底图，
剩下的就是小图形；再按格线位置定出小图形在框内第几行、第几列：
正方形、圆按外接矩形三等分；三角形的行按横线位置，列按该高度处横截面三等分
（内部两条线从顶点连到底边三等分点，任何高度都把横截面三等分）。
"""
import numpy as np
from PIL import Image
from scipy import ndimage

SRC = "/home/user/xing-ce1/广东/行测/2013-2021/assets/GD2020-XZ/GD2020-XZ-p07-i01.png"
g = np.array(Image.open(SRC).convert("L")).astype(int)
dark = g < 140
TX = [46, 227, 409, 590]          # 九宫格竖线
TY = [7, 188, 369, 551]           # 九宫格横线
OX = [7, 162, 318, 474, 629]      # 选项框竖线
OY = (583, 716)
PANELS = {}
SHAPE = {(0, 0): "圆", (0, 1): "三角", (0, 2): "方", (1, 0): "三角", (1, 1): "方", (1, 2): "圆",
         (2, 0): "方", (2, 1): "圆", "A": "三角", "B": "三角", "C": "三角", "D": "三角"}
for r in range(3):
    for c in range(3):
        if (r, c) != (2, 2):
            PANELS[(r, c)] = (TX[c], TY[r], TX[c + 1], TY[r + 1])
for i, k in enumerate("ABCD"):
    PANELS[k] = (OX[i], OY[0], OX[i + 1], OY[1])


def frame_box(k):
    x0, y0, x1, y1 = PANELS[k]
    m = dark[y0 + 4:y1 - 3, x0 + 4:x1 - 3]
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    big = int(np.argmax(ndimage.sum(m, lab, range(1, n + 1)))) + 1
    ys, xs = np.nonzero(lab == big)
    return x0 + 4 + xs.min(), y0 + 4 + ys.min(), x0 + 4 + xs.max(), y0 + 4 + ys.max()


def crops(keys):
    boxes = {k: frame_box(k) for k in keys}
    w = max(b[2] - b[0] for b in boxes.values()) + 1
    h = max(b[3] - b[1] for b in boxes.values()) + 1
    return {k: dark[b[1]:b[1] + h, b[0]:b[0] + w] for k, b in boxes.items()}


def locate(shape, keys):
    cs = crops(keys)
    common = np.logical_and.reduce([ndimage.binary_dilation(c, iterations=1) for c in cs.values()])
    base = ndimage.binary_dilation(common, iterations=1)
    out = {}
    for k, c in cs.items():
        rest = c & ~base
        lab, n = ndimage.label(rest, structure=np.ones((3, 3)))
        h, w = c.shape
        # 三角形外框：横线所在行（横截面几乎全黑）
        hy = []
        if shape == "三角":
            full = max(np.ptp(np.nonzero(common[y])[0]) for y in range(h) if common[y].any())
            for y in range(4, h - 4):
                xs = np.nonzero(common[y])[0]
                # 顶点附近几条线挤在一起整行都黑，不算横线：横截面至少要有底边宽度的30%
                if len(xs) and np.ptp(xs) > 0.3 * full and common[y, xs.min():xs.max() + 1].mean() > 0.85:
                    if not hy or y - hy[-1][-1] > 2:
                        hy.append([y])
                    else:
                        hy[-1].append(y)
            hy = [np.mean(v) for v in hy if np.mean(v) < h - 6]   # 去掉底边
        blobs = []
        for i in range(1, n + 1):
            yy, xx = np.nonzero(lab == i)
            if len(yy) < 6:
                continue
            cy, cx = yy.mean(), xx.mean()
            if shape == "三角":
                row = sum(cy > v for v in hy)
                xs = np.nonzero(common[int(round(cy))])[0]
                col = int(3 * (cx - xs.min()) / (xs.max() - xs.min() + 1))
            else:
                row, col = int(3 * cy / h), int(3 * cx / w)
            blobs.append(((row, col), len(yy), (yy.max() - yy.min() + 1, xx.max() - xx.min() + 1)))
        out[k] = sorted(blobs)
    return out


if __name__ == "__main__":
    res = {}
    for shape in ("圆", "方", "三角"):
        res.update(locate(shape, [k for k in PANELS if SHAPE[k] == shape]))
    for k in PANELS:
        name = f"第{k[0] + 1}行第{k[1] + 1}幅" if isinstance(k, tuple) else f"选项{k}"
        cells = "".join(f"（框内{p[0] + 1}行{p[1] + 1}列，{px}像素，高{hw[0]}宽{hw[1]}）" for p, px, hw in res[k])
        pos = sorted({p for p, _, _ in res[k]})
        if len(pos) == 1:
            rel = "重叠"
        else:
            d = abs(pos[0][1] - pos[1][1])
            rel = ("相邻" if d == 1 else "隔一格") if pos[0][0] == pos[1][0] else "不在同一行"
        print(f"{name}（{SHAPE[k]}框）：{cells} → {rel}")
    print("\n同一格里有两块（一大一小或大块套小块）即两个小图形重叠。规律：第k行各图的小图形都在框内第k行；"
          "每行三幅图里两个小图形的关系为相邻、重叠、隔一格各一次（第三行已有隔一格、相邻），"
          "问号处应在框内第3行且重叠，只有B。")
