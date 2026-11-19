# -*- coding: utf-8 -*-
"""M09 第47题（GD2018-Q036）：4×4方格图中灰格、白格的连通块数。

从题图按格线位置读出每格灰/白（取格子中心17×17像素的平均灰度），再数：
白格被灰格分成几块（边相连算一块）、灰格几块、灰格个数。
"""
import numpy as np
from PIL import Image
from scipy import ndimage

SRC = "/home/user/xing-ce1/广东/行测/2013-2021/assets/GD2018/GD2018-p05-i04.png"
im = np.array(Image.open(SRC).convert("L")).astype(int)
H, W = im.shape
dark = im < 80


def group(xs):
    g, cur = [], []
    for x in xs:
        if cur and x - cur[-1] > 1:
            g.append((cur[0], cur[-1])); cur = []
        cur.append(x)
    if cur:
        g.append((cur[0], cur[-1]))
    return g


def cols(y0, y1, th=100):
    cs = dark[y0:y1].sum(0)
    return [x for x in range(W) if cs[x] > th]


def rows(x0, x1, th=100):
    rs = dark[:, x0:x1].sum(1)
    return [y for y in range(H) if rs[y] > th]


def read(x0, x1, ylo, yhi):
    xs = group([x for x in cols(ylo + 3, yhi - 3) if x0 - 3 <= x <= x1 + 3])
    ys = group([y for y in rows(x0 + 2, x1 - 2) if ylo <= y <= yhi])
    xc = [(xs[i][1] + xs[i + 1][0]) // 2 for i in range(len(xs) - 1)]
    yc = [(ys[i][1] + ys[i + 1][0]) // 2 for i in range(len(ys) - 1)]
    return np.array([[im[y - 8:y + 9, x - 8:x + 9].mean() < 200 for x in xc] for y in yc])


# 各小图方格区域（外框线之间），由列、行的暗像素统计找出
PANELS = {"图1": (32, 204, 25, 215), "图2": (258, 430, 25, 215), "图3": (484, 656, 25, 215), "图4": (700, 872, 25, 215),
          "A": (141, 313, 298, 490), "B": (367, 539, 298, 490), "C": (588, 760, 298, 490), "D": (814, 986, 298, 490)}

if __name__ == "__main__":
    print("图/选项  方格（■灰 □白）            白块数  灰块数  灰格数")
    for k, (x0, x1, y0, y1) in PANELS.items():
        a = read(x0, x1, y0, y1)
        assert a.shape == (4, 4), (k, a.shape)
        pic = " ".join("".join("■" if v else "□" for v in r) for r in a)
        w = ndimage.label(~a)[1]
        g = ndimage.label(a)[1]
        print(f"{k:>4}    {pic}    {w}       {g}       {a.sum()}")
    print("\n白块数 1、2、3、4 → 问号处应为5，只有D符合；灰格数 3、10、8、10 无规律，选项灰格都是8个。")
