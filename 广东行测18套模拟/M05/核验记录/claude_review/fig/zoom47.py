# Extra 8x zoom of selected Q47 cells for vertex inspection
import os
from PIL import Image
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crops')
img = Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s27_p12_i00.png').convert('L')
boxes = {'q47_r2c2_z8': (170, 115, 235, 190), 'q47_r2c3_z8': (270, 115, 335, 185), 'q47_r3c2_z8': (165, 220, 240, 280)}
for k, b in boxes.items():
    c = img.crop(b); c = c.resize((c.size[0]*8, c.size[1]*8), Image.LANCZOS); c.save(os.path.join(OUT, k + '.png'))
print('ok')
