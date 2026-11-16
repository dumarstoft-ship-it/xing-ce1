# -*- coding: utf-8 -*-
"""M08 第90题：读四个选项折线图的方形拐点位置，与2019—2022年全国铁路货运总发送量同比增速逐点对照。

做法：方形标记约7×7像素、线宽约2像素；找所有 5×5 窗口全为深色的位置（线条宽度不够，只有标记能满足），
按连通块聚类取中心。纵坐标向下为正，所以数值越大 y 越小。
再把每个选项的四个 y 坐标用最小二乘拟合成 y = a + b·增速，看残差是否接近 0（只有比例完全对应才能拟合好）。
"""
import numpy as np
from PIL import Image

ASSET = "/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s23_p24_i0{}.png"
ship = {2018: 409268, 2019: 441213, 2020: 455236, 2021: 477372, 2022: 498424, 2023: 503535}
g = {y: ship[y] / ship[y - 1] - 1 for y in range(2019, 2024)}
for y in g:
    print(f"{y} 同比增速 {g[y]:.3%}")


def markers(path, k=5, thr=100):
    a = np.array(Image.open(path).convert("L")).astype(int)
    dark = a < thr
    h, w = dark.shape
    ok = np.zeros_like(dark)
    for y in range(h - k + 1):
        for x in range(w - k + 1):
            if dark[y:y + k, x:x + k].all():
                ok[y:y + k, x:x + k] = True
    # 连通块
    seen = np.zeros_like(ok)
    pts = []
    for y in range(h):
        for x in range(w):
            if ok[y, x] and not seen[y, x]:
                stack, comp = [(y, x)], []
                seen[y, x] = True
                while stack:
                    cy, cx = stack.pop()
                    comp.append((cy, cx))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and ok[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            stack.append((ny, nx))
                ys, xs = zip(*comp)
                pts.append((np.mean(xs), np.mean(ys), len(comp)))
    return sorted(pts)


def fit(yy, vals):
    A = np.vstack([np.ones(len(vals)), vals]).T
    coef, *_ = np.linalg.lstsq(A, np.array(yy), rcond=None)
    pred = A @ coef
    return coef, float(np.max(np.abs(pred - yy)))


series = {
    "2019-2022（题问）": [g[y] * 100 for y in (2019, 2020, 2021, 2022)],
    "2020-2023（错年份）": [g[y] * 100 for y in (2020, 2021, 2022, 2023)],
}
for i, opt in enumerate("ABCD"):
    pts = markers(ASSET.format(i))
    print(f"\n选项{opt}: 拐点(x, y, 像素数) =", [(round(x, 1), round(y, 1), n) for x, y, n in pts])
    yy = [p[1] for p in pts]
    order = " → ".join("高" if v == min(yy) else ("低" if v == max(yy) else f"{v:.0f}") for v in yy)
    print("  形状（y越小越高）：", order)
    if len(pts) == 4:
        for name, vals in series.items():
            coef, res = fit(yy, vals)
            print(f"  与{name}拟合：斜率 {coef[1]:.2f} 像素/百分点，最大残差 {res:.2f} 像素")
