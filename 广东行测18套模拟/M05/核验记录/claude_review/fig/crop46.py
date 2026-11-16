# Crop Q46 cells and enlarge 5x for viewing
import numpy as np, os
from PIL import Image
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crops')
im = Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s19_p12_i00.png').convert('L')
topx = [9, 106, 203, 300, 398, 495, 592]
botx = [105, 202, 300, 397, 495]
cells = {}
for i in range(6):
    cells['q46_t%d' % (i+1)] = (topx[i]+1, 8, topx[i+1]-1, 107)
for i, L in enumerate('ABCD'):
    cells['q46_%s' % L] = (botx[i]+1, 135, botx[i+1]-1, 233)
for k, box in cells.items():
    c = im.crop(box)
    c = c.resize((c.size[0]*5, c.size[1]*5), Image.LANCZOS)
    c.save(os.path.join(OUT, k + '.png'))
# Composite of row 1 (5 figures) at 4x
row = im.crop((9, 6, 495, 109)); row = row.resize((row.size[0]*3, row.size[1]*3), Image.LANCZOS); row.save(os.path.join(OUT, 'q46_row_x3.png'))
opt = im.crop((104, 132, 496, 236)); opt = opt.resize((opt.size[0]*3, opt.size[1]*3), Image.LANCZOS); opt.save(os.path.join(OUT, 'q46_opts_x3.png'))
print('done')
