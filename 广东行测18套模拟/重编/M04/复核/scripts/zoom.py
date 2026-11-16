"""Crop and upscale a region of a question figure for close inspection.

Usage: python3 zoom.py <src.png> <out.png> <x0> <y0> <x1> <y1> [scale]
"""
import sys
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = map(int, sys.argv[3:7])
scale = int(sys.argv[7]) if len(sys.argv) > 7 else 4
im = Image.open(src).convert("RGB")
crop = im.crop((x0, y0, x1, y1))
crop = crop.resize((crop.width * scale, crop.height * scale), Image.LANCZOS)
crop.save(out)
print(out, crop.size)
