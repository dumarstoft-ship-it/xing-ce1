# Q47: 9x zoom of options C and D with a light 10px grid for coordinate reading
import os
import numpy as np
from PIL import Image, ImageDraw
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crops')
img = Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s27_p12_i00.png').convert('RGB')
for L, box in {'C': (210, 340, 285, 408), 'D': (310, 345, 380, 405), 'B': (115, 340, 190, 416)}.items():
    c = img.crop(box); S = 9
    c = c.resize((c.size[0]*S, c.size[1]*S), Image.LANCZOS)
    d = ImageDraw.Draw(c)
    for gx in range(box[0] - box[0] % 10 + 10, box[2], 10):
        d.line([((gx-box[0])*S, 0), ((gx-box[0])*S, c.size[1])], fill=(255, 150, 150), width=1)
        d.text(((gx-box[0])*S+2, 2), str(gx), fill=(200, 0, 0))
    for gy in range(box[1] - box[1] % 10 + 10, box[3], 10):
        d.line([(0, (gy-box[1])*S), (c.size[0], (gy-box[1])*S)], fill=(150, 150, 255), width=1)
        d.text((2, (gy-box[1])*S+2), str(gy), fill=(0, 0, 200))
    c.save(os.path.join(OUT, 'q47_%s_grid_x9.png' % L))
print('ok')
