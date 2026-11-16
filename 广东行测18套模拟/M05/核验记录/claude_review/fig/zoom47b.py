# 12x zoom of bottom junctions of Q47 r2c3, with dark-pixel ASCII dump
import os
import numpy as np
from PIL import Image
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crops')
img = Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s27_p12_i00.png').convert('L')
b = (268, 145, 340, 185)
c = img.crop(b); c.resize((c.size[0]*12, c.size[1]*12), Image.NEAREST).save(os.path.join(OUT, 'q47_r2c3_bottom_z12.png'))
a = np.array(c)
for y in range(a.shape[0]):
    print('%3d ' % (b[1]+y) + ''.join('#' if v < 100 else ('+' if v < 180 else '.') for v in a[y]))
