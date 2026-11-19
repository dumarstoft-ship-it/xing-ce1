# -*- coding: utf-8 -*-
"""M09 第49题（GD2023-XZ-Q046）：哪个选项能与左图拼成整圆。

左图和各选项分别填充成实心区域；用RANSAC在轮廓上拟合圆弧（圆心、半径）；把选项绕自己的圆心旋转
（0°～360°，步长0.5°，再细化到0.05°）后与左图同心叠放，统计重叠像素和整圆内的空缺像素。
能拼成整圆的选项：重叠为0，空缺只剩两块之间轮廓线粗细的一条缝。另把各选项左右翻转后再试一遍，
看干扰项是不是正确拼块的镜像。
用法：python3 q49_fit.py [输出叠图的目录]
"""
import math
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

SRC = "/home/user/xing-ce1/广东/行测/2022-2026/assets/GD2023-XZ/GD2023-XZ-p10-i01.png"
g = np.array(Image.open(SRC).convert("L")).astype(float)
ink = g < 150
LEFT = (0, 40, 340, 340)
BOXES = {"A": (356, 34, 665, 356), "B": (672, 34, 980, 356), "C": (987, 34, 1295, 356), "D": (1302, 34, 1608, 356)}
H = W = 400


def piece(box):
    x0, y0, x1, y1 = box
    sub = ink[y0:y1, x0:x1]
    lab, n = ndimage.label(~ndimage.binary_dilation(sub, iterations=1))
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    best = max((i for i in range(1, n + 1) if i not in border), key=lambda i: (lab == i).sum())
    inside = lab == best
    return ndimage.binary_fill_holes(inside | ndimage.binary_dilation(inside, iterations=2) & sub)


def fit_circle(mask, rmin=110, rmax=170, iters=4000, tol=1.5, seed=0):
    edge = mask & ~ndimage.binary_erosion(mask)
    ys, xs = np.nonzero(edge)
    pts = np.c_[xs, ys].astype(float)
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(iters):
        (x1, y1), (x2, y2), (x3, y3) = pts[rng.choice(len(pts), 3, replace=False)]
        d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        if abs(d) < 1e-6:
            continue
        ux = ((x1 * x1 + y1 * y1) * (y2 - y3) + (x2 * x2 + y2 * y2) * (y3 - y1) + (x3 * x3 + y3 * y3) * (y1 - y2)) / d
        uy = ((x1 * x1 + y1 * y1) * (x3 - x2) + (x2 * x2 + y2 * y2) * (x1 - x3) + (x3 * x3 + y3 * y3) * (x2 - x1)) / d
        r = math.hypot(x1 - ux, y1 - uy)
        if not rmin <= r <= rmax:
            continue
        inl = np.abs(np.hypot(pts[:, 0] - ux, pts[:, 1] - uy) - r) < tol
        if best is None or inl.sum() > best[0]:
            best = (inl.sum(), inl)
    inl = best[1]
    x, y = pts[inl, 0], pts[inl, 1]
    D, E, F = np.linalg.lstsq(np.c_[x, y, np.ones(len(x))], -(x * x + y * y), rcond=None)[0]
    cx, cy = -D / 2, -E / 2
    return cx, cy, math.sqrt(cx * cx + cy * cy - F)


def place(mask, cx, cy, ang):
    yy, xx = np.mgrid[0:H, 0:W]
    dx, dy = xx - W / 2, yy - H / 2
    a = math.radians(ang)
    sx = math.cos(a) * dx + math.sin(a) * dy + cx
    sy = -math.sin(a) * dx + math.cos(a) * dy + cy
    return ndimage.map_coordinates(mask.astype(float), [sy, sx], order=1, cval=0) > 0.5


def best_fit(M, Lc, disk):
    cx, cy, r = fit_circle(M)
    best = None
    for t in np.arange(0, 360, 0.5):
        Mc = place(M, cx, cy, t)
        sc = ((Mc & Lc).sum(), (disk & ~(Mc | Lc)).sum())
        if best is None or sum(sc) < sum(best[1]):
            best = (t, sc)
    for t in np.arange(best[0] - 0.5, best[0] + 0.5, 0.05):
        Mc = place(M, cx, cy, t)
        sc = ((Mc & Lc).sum(), (disk & ~(Mc | Lc)).sum())
        if sum(sc) < sum(best[1]):
            best = (t, sc)
    return r, best, place(M, cx, cy, best[0])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else None
    L = piece(LEFT)
    cxL, cyL, rL = fit_circle(L)
    Lc = place(L, cxL, cyL, 0)
    yy, xx = np.mgrid[0:H, 0:W]
    disk = np.hypot(xx - W / 2, yy - H / 2) <= rL
    print(f"左图圆弧半径 {rL:.1f} 像素，整圆 {disk.sum()} 像素")
    for flip in (False, True):
        print("== 选项左右翻转后" if flip else "== 选项原样（只旋转）")
        for k, box in BOXES.items():
            M = piece(box)
            if flip:
                M = M[:, ::-1].copy()
            r, (t, (over, gap)), Mc = best_fit(M, Lc, disk)
            print(f"  {k}：半径 {r:.1f}，最佳旋转 {t:.2f}°，重叠 {over} 像素，空缺 {gap} 像素（占整圆 {100 * (over + gap) / disk.sum():.1f}%）")
            if out:
                img = np.full((H, W, 3), 255, np.uint8)
                img[Lc] = (150, 190, 255); img[Mc] = (255, 200, 140); img[Lc & Mc] = (200, 0, 0)
                img[disk & ~(Lc | Mc)] = (0, 0, 0)
                Image.fromarray(img).save(f"{out}/q49_{'flip_' if flip else ''}{k}.png")
    print("A：重叠为0，空缺只是两块之间轮廓线宽的一条缝，能拼成整圆；B、C、D无论是否翻转都有成片的重叠和空缺。")
