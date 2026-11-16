# Q49: enlarge solid and net
import os
from PIL import Image
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crops')
img = Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s20_p13_i00.png').convert('L')
img.crop((0, 0, 160, 150)).resize((160*5, 150*5), Image.LANCZOS).save(os.path.join(OUT, 'q49_solid_x5.png'))
img.crop((250, 0, 500, 199)).resize((250*4, 199*4), Image.LANCZOS).save(os.path.join(OUT, 'q49_net_x4.png'))
print('ok')
