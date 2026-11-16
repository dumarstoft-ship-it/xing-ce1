# Q50: enlarge solid and options
import os
from PIL import Image
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crops')
img = Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s23_p13_i00.png').convert('L')
print(img.size)
img.crop((0, 0, 150, 125)).resize((150*6, 125*6), Image.LANCZOS).save(os.path.join(OUT, 'q50_solid_x6.png'))
img.crop((145, 0, 600, 154)).resize((455*2, 154*2), Image.LANCZOS).save(os.path.join(OUT, 'q50_opts_x2.png'))
print('ok')
