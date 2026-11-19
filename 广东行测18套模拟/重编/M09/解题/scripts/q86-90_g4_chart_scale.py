# -*- coding: utf-8 -*-
"""第86—90题材料的两张原卷图是否按比例绘制（只影响观感，不影响作答；数值以标注为准）。
图2柱状图：量柱顶像素高度，以2018年两根柱定比例，与柱顶标注对照。
图1折线图：量各年圆点高度，按纵轴刻度折算，与标注的增速对照。"""
import numpy as np
from PIL import Image

p = '/home/user/xing-ce1/广东/行测/2022-2026/assets/GD2023-XJ/GD2023-XJ-p28-i02.png'
g = np.asarray(Image.open(p).convert('L'), dtype=float)
H, W = g.shape
# 横轴：柱底所在行（最长的深色水平线）；比例尺用2018年两根柱子的高度与标注值确定
rows = [(y, np.mean(g[y, 220:1680] < 100)) for y in range(H // 2, H)]
axis_y = max(rows, key=lambda t: t[1])[0]
labels = {'mobile': [5984, 6096, 6204, 6381, 6397], 'new': [1084, 1374, 1737, 2372, 3072]}


def bar_top(x0, x1, dark):
    col = g[:axis_y, x0:x1]
    m = (col < 90) if dark else ((col > 110) & (col < 190))
    frac = m.mean(axis=1)
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

# 图1折线：量各年圆点中心的高度，按纵轴刻度（0%在第455行，每2%约72.6像素）折算
p1 = '/home/user/xing-ce1/广东/行测/2022-2026/assets/GD2023-XJ/GD2023-XJ-p28-i01.png'
g1 = np.asarray(Image.open(p1).convert('L'), dtype=float)
y0, per_pct = 455.0, (455.0 - 92.0) / 10.0   # 0%与10%刻度行
for yr, x0, lab in zip(range(2018, 2023), (330, 635, 915, 1210, 1497), (2.9, 0.5, 3.9, 8.1, 8.0)):
    sub = g1[60:470, x0 - 15:x0 + 15]
    ys = np.nonzero((sub < 60).sum(axis=1) >= 8)[0] + 60
    c = ys.mean()
    print('折线 %d年 标注%.1f%% 圆点画在%.2f%%' % (yr, lab, (y0 - c) / per_pct))
