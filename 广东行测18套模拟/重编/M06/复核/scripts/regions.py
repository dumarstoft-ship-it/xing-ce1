"""通用：把题图某个面板按黑色线条切成若干封闭区域，输出每个区域的面积、质心、颜色（灰/白）。
用于第47题（黑白/灰色区域类）。
"""
import sys
import numpy as np
from PIL import Image
from collections import deque


def label(mask):
    h, w = mask.shape
    lab = -np.ones((h, w), int)
    comps = []
    for y in range(h):
        for x in range(w):
            if mask[y, x] and lab[y, x] < 0:
                q = deque([(y, x)])
                lab[y, x] = len(comps)
                pts = []
                while q:
                    cy, cx = q.popleft()
                    pts.append((cy, cx))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and lab[ny, nx] < 0:
                            lab[ny, nx] = len(comps)
                            q.append((ny, nx))
                comps.append(pts)
    return lab, comps


def regions(img_path, box, line_thr=80, min_area=15):
    x0, y0, x1, y1 = box
    g = np.array(Image.open(img_path).convert('L')).astype(float)[y0:y1, x0:x1]
    nonline = g >= line_thr
    lab, comps = label(nonline)
    out = []
    for i, pts in enumerate(comps):
        if len(pts) < min_area:
            continue
        ys = np.array([p[0] for p in pts]); xs = np.array([p[1] for p in pts])
        touches = ys.min() == 0 or xs.min() == 0 or ys.max() == g.shape[0] - 1 or xs.max() == g.shape[1] - 1
        vals = g[ys, xs]
        med = np.median(vals)
        color = 'gray' if med < 200 else 'white'
        out.append(dict(id=i, area=len(pts), cy=ys.mean() + y0, cx=xs.mean() + x0,
                        color=color, med=med, outside=touches))
    return out


if __name__ == '__main__':
    p = sys.argv[1]
    box = tuple(map(int, sys.argv[2:6]))
    for r in regions(p, box):
        print(r)
