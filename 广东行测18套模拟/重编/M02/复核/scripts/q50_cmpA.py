import sys
sys.path.insert(0, '.')
from q50_render import render, full
from PIL import Image
import numpy as np
SRC = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s17_p13_i00.png'
src = Image.open(SRC).convert('L')
out = sys.argv[1]
missA = {(0,1,0),(2,1,0),(2,1,1),(0,0,0),(2,0,0)}
vox = full() - missA
off = (25, 140)
r = render(vox, 33, 209.5, size=(80, 75), off=off)
o = src.crop((off[0], off[1], off[0] + 80, off[1] + 75))
canvas = Image.new('L', (80 * 8 * 2 + 20, 75 * 8), 255)
canvas.paste(o.resize((640, 600), Image.NEAREST), (0, 0))
canvas.paste(r.resize((640, 600), Image.NEAREST), (660, 0))
canvas.save(out)
a = np.array(o).astype(float); b = np.array(r).astype(float)
print('corr', np.corrcoef(a.ravel(), b.ravel())[0, 1])
