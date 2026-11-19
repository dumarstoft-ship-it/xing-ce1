# -*- coding: utf-8 -*-
"""第86—90组材料图2：量柱顶像素高度，与柱顶标注数值对照，看原图是否按比例绘制（只影响观感，不影响作答）。"""
import numpy as np
from PIL import Image

p = '/home/user/xing-ce1/广东/行测/2022-2026/assets/GD2023-XJ/GD2023-XJ-p28-i02.png'
g = np.asarray(Image.open(p).convert('L'), dtype=float)
H, W = g.shape
# 纵轴刻度：找“0”与“7000”刻度线所在行——用左侧纵轴线右边的短刻度难以识别，改用柱底（横轴）与已知柱顶回归
# 横轴：柱底所在行（最长的深色水平线）
rows = [(y, np.mean(g[y, 220:1680] < 100)) for y in range(H // 2, H)]
axis_y = max(rows, key=lambda t: t[1])[0]
labels = {'mobile': [5984, 6096, 6204, 6381, 6397], 'new': [1084, 1374, 1737, 2372, 3072]}


def bar_top(x0, x1, dark):
    col = g[:axis_y, x0:x1]
    m = (col < 90) if dark else ((col > 110) & (col < 190))
    frac = m.mean(axis=1)
    ys = np.nonzero(frac > 0.6)[0]
    # 取紧贴横轴向上连续的那一段的最高点
    top = axis_y
    for y in range(axis_y - 3, 0, -1):
        if frac[y] > 0.6:
            top = y
        elif axis_y - y > 15 and frac[y] < 0.2:
            break
    return top

# 柱子的大致水平位置（按图片目测：每组深色柱在左、灰柱在右）
dark_x = [(300, 360), (600, 660), (890, 950), (1180, 1235), (1475, 1530)]
gray_x = [(392, 450), (690, 750), (982, 1040), (1275, 1335), (1565, 1622)]
tops_d = [bar_top(a, b, True) for a, b in dark_x]
tops_g = [bar_top(a, b, False) for a, b in gray_x]
hd = [axis_y - t for t in tops_d]
hg = [axis_y - t for t in tops_g]
# 以2018年两根柱子定比例（像素/亿元）
k = (hd[0] / 5984 + hg[0] / 1084) / 2
print('横轴行', axis_y, '比例 %.4f 像素/亿元' % k)
for name, hs, labs in (('移动数据流量', hd, labels['mobile']), ('新兴业务', hg, labels['new'])):
    for yr, h, v in zip(range(2018, 2023), hs, labs):
        print('%s %d年 标注%d 按柱高折算%.0f 偏差%+.1f%%' % (name, yr, v, h / k, (h / k / v - 1) * 100))
