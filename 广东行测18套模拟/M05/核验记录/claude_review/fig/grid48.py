# Q48: locate rows and glyph columns
import numpy as np, os
from PIL import Image
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crops')
img = Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s31_p12_i00.png').convert('L')
im = np.array(img); H, W = im.shape
dark = im < 128
rows = dark.sum(1)
print('H,W', H, W)
# row bands
band = []; inb = False
for y in range(H):
    if rows[y] > 0 and not inb: s = y; inb = True
    if rows[y] == 0 and inb: band.append((s, y-1)); inb = False
if inb: band.append((s, H-1))
print('row bands:', band)
for (a, b) in band:
    cols = dark[a:b+1].sum(0)
    seg = []; inb = False
    for x in range(W):
        if cols[x] > 0 and not inb: s = x; inb = True
        if cols[x] == 0 and inb: seg.append((s, x-1)); inb = False
    if inb: seg.append((s, W-1))
    print((a, b), 'col segs:', seg)
img.resize((W*3, H*3), Image.LANCZOS).save(os.path.join(OUT, 'q48_x3.png'))
