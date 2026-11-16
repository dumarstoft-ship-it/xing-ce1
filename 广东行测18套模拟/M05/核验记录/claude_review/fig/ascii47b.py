# Q47: ASCII dumps of selected grid cells (original pixels)
import sys
import numpy as np
from PIL import Image
im = np.array(Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s27_p12_i00.png').convert('L'))
xs = [51, 150, 250, 350]; ys = [6, 100, 200, 300]
for name in sys.argv[1:]:
    r, c = int(name[1]) - 1, int(name[3]) - 1
    x0, x1, y0, y1 = xs[c]+4, xs[c+1]-3, ys[r]+4, ys[r+1]-3
    sub = im[y0:y1, x0:x1]
    rows = [y for y in range(sub.shape[0]) if (sub[y] < 190).any()]
    print('==', name, 'x0=%d' % x0)
    for y in range(max(0, rows[0]-1), min(sub.shape[0], rows[-1]+2)):
        print('%3d ' % (y0+y) + ''.join('#' if v < 110 else ('+' if v < 190 else '.') for v in sub[y]))
