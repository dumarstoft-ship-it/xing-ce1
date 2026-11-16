"""第47题：对第三行与四个选项的五个外围五边形取中心附近 5x5 像素均值，<100 记为黑。
五边形位置相对面板左上角（由放大图读出）：上、左上、右上、左下、右下。
用法: python3 q47_sample.py <png>
"""
import sys
import numpy as np
from PIL import Image

a = np.array(Image.open(sys.argv[1]).convert("L")).astype(float)
d = a < 128
# 选项面板竖线 & 第三行面板
def vlines(y0, y1, x0=0, x1=None):
    x1 = x1 or a.shape[1]
    cf = d[y0:y1, x0:x1].mean(axis=0)
    xs = [x0 + i for i, v in enumerate(cf) if v > 0.8]
    g = []
    for x in xs:
        if g and x - g[-1][-1] <= 1: g[-1].append(x)
        else: g.append([x])
    return [int(np.mean(t)) for t in g]

print("row3 vlines", vlines(205, 300), "opt vlines", vlines(335, 425))
# 相对面板左边线、上边线的偏移（像素），由放大图读出
offs = {"上": (50, 28), "左上": (28, 50), "右上": (77, 50), "左下": (38, 82), "右下": (68, 82)}
def read(px, py):
    out = {}
    for k, (dx, dy) in offs.items():
        x, y = px + dx, py + dy
        out[k] = "黑" if a[y - 2:y + 3, x - 2:x + 3].mean() < 100 else "白"
    return out
rv = vlines(205, 300); ov = vlines(335, 425)
hl = lambda x0, x1, y0, y1: [y0 + i for i, v in enumerate(d[y0:y1, x0:x1].mean(axis=1)) if v > 0.8]
print("row3 hlines", hl(rv[0], rv[-1], 180, 320), "opt hlines", hl(ov[0], ov[-1], 320, 440))
r_top = hl(rv[0], rv[-1], 180, 320)[0]
o_top = hl(ov[0], ov[-1], 320, 440)[0]
for i, nm in enumerate(["第三行图1", "第三行图2"]):
    print(nm, read(rv[i], r_top))
for i, nm in enumerate("ABCD"):
    print("选项", nm, read(ov[i], o_top))
