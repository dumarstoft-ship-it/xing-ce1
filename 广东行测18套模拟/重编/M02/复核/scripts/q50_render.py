"""Q50 helper: render voxel sets in the cabinet projection used by s17_p13_i00.png
so a reconstruction can be checked against the drawing.
Projection (fitted from the drawing): cube (x,y,z) [x right, y up, z = depth/back]
  front face left  = X0 + W*x + DX*z,   top = YB - H*(y+1) - DY*z
"""
import numpy as np
from PIL import Image, ImageDraw

W, H, DX, DY = 16.7, 15.7, 4.5, 4.7

def render(vox, X0, YB, size=(80, 75), off=(0, 0), ss=4):
    img = Image.new('L', (size[0] * ss, size[1] * ss), 255)
    d = ImageDraw.Draw(img)
    def P(px, py):
        return ((px - off[0]) * ss, (py - off[1]) * ss)
    for (x, y, z) in sorted(vox, key=lambda v: (-v[2], v[1], v[0])):
        l = X0 + W * x + DX * z
        t = YB - H * (y + 1) - DY * z
        r, b = l + W, t + H
        front = [P(l, t), P(r, t), P(r, b), P(l, b)]
        top = [P(l, t), P(r, t), P(r + DX, t - DY), P(l + DX, t - DY)]
        right = [P(r, t), P(r + DX, t - DY), P(r + DX, b - DY), P(r, b)]
        lw = int(1.6 * ss)
        d.polygon(right, fill=205, outline=0)
        d.line(right + [right[0]], fill=0, width=lw)
        d.polygon(top, fill=255, outline=0)
        d.line(top + [top[0]], fill=0, width=lw)
        d.polygon(front, fill=255, outline=0)
        d.line(front + [front[0]], fill=0, width=lw)
    return img.resize(size, Image.LANCZOS)

def full():
    return {(x, y, z) for x in range(3) for y in range(3) for z in range(3)}
