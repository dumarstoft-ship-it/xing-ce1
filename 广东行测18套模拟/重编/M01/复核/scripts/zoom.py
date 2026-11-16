"""放大题图局部，便于目视检查。
用法: python3 zoom.py <src.png> <out.png> <scale> [x0 y0 x1 y1]
"""
import sys
from PIL import Image

src, out, scale = sys.argv[1], sys.argv[2], float(sys.argv[3])
im = Image.open(src).convert("RGB")
if len(sys.argv) >= 8:
    x0, y0, x1, y1 = map(int, sys.argv[4:8])
    im = im.crop((x0, y0, x1, y1))
w, h = im.size
im = im.resize((int(w * scale), int(h * scale)), Image.NEAREST)
im.save(out)
print(out, im.size)
