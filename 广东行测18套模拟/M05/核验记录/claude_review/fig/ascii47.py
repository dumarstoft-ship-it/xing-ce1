# Q47: ASCII dumps of option cells C and D (original pixels) for vertex analysis
import sys
import numpy as np
from PIL import Image
im = np.array(Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s27_p12_i00.png').convert('L'))
bx = [6, 103, 200, 297, 394]
which = sys.argv[1:] or ['C', 'D']
for L in which:
    i = 'ABCD'.index(L)
    x0, x1 = bx[i]+4, bx[i+1]-3
    sub = im[338:422, x0:x1]
    print('== option', L, 'x0=%d y0=338' % x0)
    for y in range(sub.shape[0]):
        print('%3d ' % (338+y) + ''.join('#' if v < 110 else ('+' if v < 190 else '.') for v in sub[y]))
