"""第46题：9x9黑白格，验证"整体每次向上1格、向左1格循环平移"规律并比对四个选项。"""
import os
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grid_extract import extract, show

P = "/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s21_p11_i00.png"
TOP = [(10, 102), (107, 200), (205, 298), (303, 395), (400, 492)]
OPT = {"A": (110, 200), "B": (208, 297), "C": (306, 395), "D": (403, 492)}

g = np.array(Image.open(P).convert('L')).astype(float)

def grid_with_margin(x0, x1, y0, y1):
    grid, v, h = extract(P, x0, x1, y0, y1)
    # 记录每格均值，检查有无临界格
    means = []
    for r in range(len(h) - 1):
        for c in range(len(v) - 1):
            ya, yb = h[r][2] + 1 + y0, h[r + 1][1] - 1 + y0
            xa, xb = v[c][2] + 1 + x0, v[c + 1][1] - 1 + x0
            means.append(g[ya + 1:yb, xa + 1:xb].mean())
    means = np.array(means)
    amb = ((means > 60) & (means < 200)).sum()
    return np.array(grid), amb

panels = []
for x0, x1 in TOP:
    gr, amb = grid_with_margin(x0, x1, 12, 104)
    assert gr.shape == (9, 9), gr.shape
    panels.append(gr)
    print(show(gr), ' 临界格数', amb, ' 黑格数', gr.sum())
    print()

def shift(a, dr, dc):
    return np.roll(np.roll(a, dr, axis=0), dc, axis=1)

# 检验相邻两幅的平移关系
for i in range(4):
    hits = [(dr, dc) for dr in range(-4, 5) for dc in range(-4, 5)
            if np.array_equal(shift(panels[i], dr, dc), panels[i + 1])]
    print(f'图{i+1}->图{i+2} 满足的循环平移(行,列)：', hits)

pred = shift(panels[4], -1, -1)
print('\n预测第6幅：')
print(show(pred))
for k, (x0, x1) in OPT.items():
    gr, amb = grid_with_margin(x0, x1, 140, 234)
    assert gr.shape == (9, 9), (k, gr.shape)
    diff = np.argwhere(gr != pred)
    print(f'\n选项{k} 临界格{amb} 黑格数{gr.sum()} 与预测不同的格(行,列)：', diff.tolist())
    print(show(gr))
