"""逐行列出暗像素段及其加权中心，用于精确描出线条。
用法: python3 trace_rows.py <png> x0 x1 y0 y1 [thr]
"""
import sys
from PIL import Image
import numpy as np

a = np.array(Image.open(sys.argv[1]).convert("L")).astype(int)
x0, x1, y0, y1 = map(int, sys.argv[2:6])
thr = int(sys.argv[6]) if len(sys.argv) > 6 else 128
for y in range(y0, y1):
    out, s = [], None
    for x in range(x0, x1):
        d = a[y, x] < thr
        if d and s is None:
            s = x
        if not d and s is not None:
            out.append((s, x - 1)); s = None
    if s is not None:
        out.append((s, x1 - 1))
    cs = []
    for s, e in out:
        xs = np.arange(s, e + 1); w = 255 - a[y, s:e + 1]
        cs.append(round(float((xs * w).sum() / w.sum()), 1))
    print(y, out, cs)
