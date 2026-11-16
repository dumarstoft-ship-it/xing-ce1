"""第46题核验：对题图每个小格做二值化+连通域标记，统计封闭区域（面）的个数，
并用轮廓角点粗估每个面的边数。仅依赖 Pillow + numpy。

用法：python3 q46_regions.py [题图路径]
"""
import sys
from collections import deque

import numpy as np
from PIL import Image

IMG = sys.argv[1] if len(sys.argv) > 1 else \
    "/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s17_p11_i00.png"

im = Image.open(IMG).convert("L")
A = np.array(im)

# 小格边框坐标（由列/行暗像素投影得到）
TOP_XS = [4, 102, 201, 299, 397, 496]
TOP_Y = (5, 106)
OPT_XS = [102, 201, 299, 397, 496]
OPT_Y = (131, 232)

SCALE = 4   # 放大后再二值化，避免细缝漏连


def label_white(mask):
    """4-连通标记白色像素，返回 (labels, n)。"""
    h, w = mask.shape
    lab = np.zeros((h, w), dtype=np.int32)
    n = 0
    for y in range(h):
        for x in range(w):
            if mask[y, x] and lab[y, x] == 0:
                n += 1
                q = deque([(y, x)])
                lab[y, x] = n
                while q:
                    cy, cx = q.popleft()
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and lab[ny, nx] == 0:
                            lab[ny, nx] = n
                            q.append((ny, nx))
    return lab, n


def count_regions(box, thr=160, min_area=30):
    x0, y0, x1, y1 = box
    # 去掉小格自身的边框：向内缩 4px
    sub = im.crop((x0 + 4, y0 + 4, x1 - 3, y1 - 3))
    sub = sub.resize((sub.width * SCALE, sub.height * SCALE), Image.BILINEAR)
    arr = np.array(sub)
    white = arr > thr
    lab, n = label_white(white)
    # 与外圈相连的白色区域是背景
    border = set(np.unique(np.concatenate([lab[0, :], lab[-1, :], lab[:, 0], lab[:, -1]])))
    regions = []
    for k in range(1, n + 1):
        if k in border:
            continue
        area = int((lab == k).sum())
        if area < min_area * SCALE * SCALE / 4:
            continue
        ys, xs = np.nonzero(lab == k)
        regions.append((area // (SCALE * SCALE), (int(xs.mean()) // SCALE, int(ys.mean()) // SCALE)))
    return regions


if __name__ == "__main__":
    names = ["图1", "图2", "图3", "图4", "图5"]
    for i, nm in enumerate(names):
        r = count_regions((TOP_XS[i], TOP_Y[0], TOP_XS[i + 1], TOP_Y[1]))
        print(nm, "面数 =", len(r), "各面(面积,重心) =", r)
    for i, nm in enumerate("ABCD"):
        r = count_regions((OPT_XS[i], OPT_Y[0], OPT_XS[i + 1], OPT_Y[1]))
        print(nm, "面数 =", len(r), "各面(面积,重心) =", r)
