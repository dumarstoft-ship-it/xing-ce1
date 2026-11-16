# Q48: segment glyphs inside box (y 9..79, x 40..491), print ASCII of every glyph in box and options
import numpy as np, os
from PIL import Image
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crops')
img = Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s31_p12_i00.png').convert('L')
im = np.array(img); dark = im < 128
def colsegs(a, b, x0, x1):
    cols = dark[a:b+1, x0:x1].sum(0); seg = []; inb = False
    for x in range(len(cols)):
        if cols[x] > 0 and not inb: s = x; inb = True
        if cols[x] == 0 and inb: seg.append((s+x0, x-1+x0)); inb = False
    if inb: seg.append((s+x0, x1-1))
    return seg
box_segs = colsegs(9, 79, 41, 491)
print('box glyph x-segs:', box_segs)
rowsb = dark[9:80, 41:491].sum(1)
ys = [y+9 for y in range(len(rowsb)) if rowsb[y] > 0]
print('box glyph y-range', ys[0], ys[-1])
def show(name, a, b, x0, x1):
    sub = dark[a:b+1, x0:x1+1]
    print('==', name, 'x[%d,%d] y[%d,%d]' % (x0, x1, a, b))
    for row in sub:
        print('   ' + ''.join('#' if v else '.' for v in row))
for i, (x0, x1) in enumerate(box_segs):
    show('box%d' % (i+1), ys[0], ys[-1], x0, x1)
rowband = {'A': (106, 140), 'B': (163, 197), 'C': (221, 255), 'D': (278, 312)}
for L, (a, b) in rowband.items():
    segs = colsegs(a, b, 50, 500)
    for i, (x0, x1) in enumerate(segs):
        show('%s%d' % (L, i+1), a, b, x0, x1)
# also save enlarged crops
img.crop((38, 6, 495, 83)).resize(((495-38)*3, 77*3), Image.LANCZOS).save(os.path.join(OUT, 'q48_box_x3.png'))
img.crop((0, 100, 500, 318)).resize((500*2, 218*2), Image.LANCZOS).save(os.path.join(OUT, 'q48_opts_x2.png'))
