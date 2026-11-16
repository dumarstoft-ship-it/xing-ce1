# Q50: 10x nearest-neighbour zoom of the solid's central part + ASCII dump of the whole solid
import os
import numpy as np
from PIL import Image
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crops')
img = Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s23_p13_i00.png').convert('L')
img.crop((60, 35, 135, 105)).resize((75*10, 70*10), Image.LANCZOS).save(os.path.join(OUT, 'q50_mid_x10.png'))
a = np.array(img.crop((20, 15, 132, 108)))
for y in range(a.shape[0]):
    print('%3d ' % (15+y) + ''.join('#' if v < 110 else ('+' if v < 190 else '.') for v in a[y]))
