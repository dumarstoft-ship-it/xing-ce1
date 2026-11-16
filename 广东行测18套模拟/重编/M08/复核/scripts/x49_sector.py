# 第49题：按像素打印扇形题图（原图坐标），用于核对虚线端点位置
import sys
from PIL import Image
import numpy as np
p = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s24_p11_i01.png'
im = np.array(Image.open(p).convert('L')).astype(int)
x0, x1, y0, y1 = [int(v) for v in sys.argv[1:5]] if len(sys.argv) > 4 else (215, 285, 0, 65)
print('     ' + ''.join(str((x // 10) % 10) for x in range(x0, x1)))
print('     ' + ''.join(str(x % 10) for x in range(x0, x1)))
for y in range(y0, y1):
    print(f'{y:4d} ' + ''.join('#' if im[y, x] < 100 else ('+' if im[y, x] < 180 else '.') for x in range(x0, x1)))
