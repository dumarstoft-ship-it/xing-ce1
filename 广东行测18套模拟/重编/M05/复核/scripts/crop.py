"""Crop and upscale a region of a question image for close inspection.
usage: python3 crop.py <src.png> <out.png> x0 y0 x1 y1 [scale]
"""
import sys
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = map(int, sys.argv[3:7])
scale = float(sys.argv[7]) if len(sys.argv) > 7 else 4
im = Image.open(src).convert("RGB")
c = im.crop((x0, y0, x1, y1))
c = c.resize((int(c.width * scale), int(c.height * scale)), Image.LANCZOS)
c.save(out)
print(out, c.size)
