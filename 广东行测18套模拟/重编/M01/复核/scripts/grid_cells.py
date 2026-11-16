"""第46题：把每个小方框里的 4x4 网格读成 0/1 矩阵（1=黑格）。
做法：对每个面板，去掉外框后取黑像素包围盒（即网格外框），等分为 4x4，
看每格中心 40% 区域的黑像素占比（>0.5 记为黑）。
再按外圈顺时针编号 0..11（从左上角起），输出黑格在外圈上的位置。
用法: python3 grid_cells.py <png>
"""
import sys
from PIL import Image
import numpy as np

im = np.array(Image.open(sys.argv[1]).convert("L"))
dark = im < 128

# 面板位置（原图坐标，目测给出外框范围，留出边距以去掉外框线）
panels = {  # 外框线位置由列/行黑像素占比>0.8 检测得到，向内收 6px
    "1": (7+6, 7+6, 102-6, 110-6), "2": (105+6, 7+6, 200-6, 110-6), "3": (203+6, 7+6, 298-6, 110-6),
    "4": (301+6, 7+6, 397-6, 110-6), "5": (400+6, 7+6, 495-6, 110-6),
    "A": (107+6, 144+6, 202-6, 246-6), "B": (205+6, 144+6, 300-6, 246-6),
    "C": (303+6, 144+6, 399-6, 246-6), "D": (402+6, 144+6, 497-6, 246-6),
}

ring = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (2, 3), (3, 3), (3, 2), (3, 1), (3, 0), (2, 0), (1, 0)]


def read_grid(x0, y0, x1, y1, n=4):
    sub = dark[y0:y1, x0:x1]
    ys, xs = np.nonzero(sub)
    gy0, gy1, gx0, gx1 = ys.min(), ys.max(), xs.min(), xs.max()
    g = np.zeros((n, n), int)
    ch = (gy1 - gy0) / n
    cw = (gx1 - gx0) / n
    for r in range(n):
        for c in range(n):
            cy0 = int(gy0 + (r + 0.3) * ch); cy1 = int(gy0 + (r + 0.7) * ch)
            cx0 = int(gx0 + (c + 0.3) * cw); cx1 = int(gx0 + (c + 0.7) * cw)
            frac = sub[cy0:cy1, cx0:cx1].mean()
            g[r, c] = 1 if frac > 0.5 else 0
    return g, (x0 + gx0, y0 + gy0, x0 + gx1, y0 + gy1)


for name, box in panels.items():
    g, bb = read_grid(*box)
    pos = [i for i, (r, c) in enumerate(ring) if g[r, c]]
    inner = int(g[1:3, 1:3].sum())
    print(f"panel {name} bbox={bb} black={g.sum()} ring_pos={pos} inner_black={inner}")
    for row in g:
        print("   ", " ".join("#" if v else "." for v in row))
