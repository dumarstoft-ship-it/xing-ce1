#!/usr/bin/env python3
"""第90题选项图点位提取：找出四个方形标记点的像素坐标，
再与2019-2022年同比增长率做线性拟合，检查哪一幅图按比例吻合。
运行：python3 -I q90_figs.py <仓库根目录>
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

root = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/user/xing-ce1")
figdir = root / "模考/2026下半年广东卷_16-33季_AI可读/assets"
names = {"A": "s23_p24_i00.png", "B": "s23_p24_i01.png", "C": "s23_p24_i02.png", "D": "s23_p24_i03.png"}

V = {2018: 409268, 2019: 441213, 2020: 455236, 2021: 477372, 2022: 498424}
G = [V[y] / V[y - 1] - 1 for y in (2019, 2020, 2021, 2022)]
print("2019-2022同比增长率(%):", [round(g * 100, 4) for g in G])


def find_markers(arr):
    """标记点是实心小方块：用 5x5 全暗窗口检测，然后按 x 聚类。"""
    dark = arr < 100
    h, w = dark.shape
    hits = []
    k = 2
    for y in range(k, h - k):
        for x in range(k, w - k):
            if dark[y - k:y + k + 1, x - k:x + k + 1].all():
                hits.append((x, y))
    # 聚类
    clusters = []
    for x, y in sorted(hits):
        for c in clusters:
            if abs(c["x"][-1] - x) <= 6 and abs(np.mean(c["y"]) - y) <= 6:
                c["x"].append(x); c["y"].append(y)
                break
        else:
            clusters.append({"x": [x], "y": [y]})
    pts = sorted((float(np.mean(c["x"])), float(np.mean(c["y"]))) for c in clusters)
    return pts


for k, n in names.items():
    im = Image.open(figdir / n).convert("L")
    arr = np.array(im)
    pts = find_markers(arr)
    print(f"\n选项{k} {n} 尺寸={im.size} 标记点(x,y)={[(round(x,1), round(y,1)) for x, y in pts]}")
    if len(pts) != 4:
        print("  标记点数≠4，需人工看图")
        continue
    ys = np.array([p[1] for p in pts])
    vals = -ys  # 图像坐标 y 向下，取负号得到“高度”
    # 线性拟合 高度 = a*g + b
    g = np.array(G) * 100
    a, b = np.polyfit(g, vals, 1)
    pred = a * g + b
    resid = vals - pred
    r = np.corrcoef(g, vals)[0, 1]
    # 走势符号
    trend = ["升" if vals[i + 1] > vals[i] else ("降" if vals[i + 1] < vals[i] else "平") for i in range(3)]
    true_trend = ["升" if G[i + 1] > G[i] else "降" for i in range(3)]
    print(f"  图形走势={trend}；真实走势={true_trend}；{'一致' if trend == true_trend else '不一致'}")
    print(f"  线性拟合斜率={a:.3f}像素/百分点，相关系数r={r:.4f}，残差(像素)={np.round(resid, 2).tolist()}")
