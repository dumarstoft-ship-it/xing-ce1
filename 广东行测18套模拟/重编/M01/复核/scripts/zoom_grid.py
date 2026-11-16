"""放大局部并叠加坐标网格（原图坐标），便于读出各棱线位置。
用法: python3 zoom_grid.py <src.png> <out.png> <scale> x0 y0 x1 y1 [step]
网格每 step 个原图像素一条细线（默认 5），每 25 像素一条较粗线并标注坐标。
"""
import sys
from PIL import Image, ImageDraw

src, out, scale = sys.argv[1], sys.argv[2], int(sys.argv[3])
x0, y0, x1, y1 = map(int, sys.argv[4:8])
step = int(sys.argv[8]) if len(sys.argv) > 8 else 5
im = Image.open(src).convert("RGB").crop((x0, y0, x1, y1))
w, h = im.size
im = im.resize((w * scale, h * scale), Image.NEAREST)
d = ImageDraw.Draw(im)
for x in range(x0 - x0 % step, x1 + 1, step):
    X = (x - x0) * scale
    if X < 0:
        continue
    col = (255, 0, 0) if x % 25 == 0 else (255, 180, 180)
    d.line([(X, 0), (X, h * scale)], fill=col, width=1)
    if x % 25 == 0:
        d.text((X + 2, 2), str(x), fill=(255, 0, 0))
for y in range(y0 - y0 % step, y1 + 1, step):
    Y = (y - y0) * scale
    if Y < 0:
        continue
    col = (0, 0, 255) if y % 25 == 0 else (180, 180, 255)
    d.line([(0, Y), (w * scale, Y)], fill=col, width=1)
    if y % 25 == 0:
        d.text((2, Y + 2), str(y), fill=(0, 0, 255))
im.save(out)
print(out, im.size)
