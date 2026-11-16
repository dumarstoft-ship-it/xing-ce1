# Enlarge source figures (read-only on repo) into scratch crops for visual inspection
import sys, os
from PIL import Image
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crops')
BASE = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/'
imgs = ['s19_p12_i00', 's27_p12_i00', 's31_p12_i00', 's20_p13_i00', 's23_p13_i00']
for name in imgs:
    im = Image.open(BASE + name + '.png')
    print(name, im.size, im.mode, im.info.get('dpi'))
    big = im.convert('L').resize((im.size[0]*3, im.size[1]*3), Image.LANCZOS)
    big.save(os.path.join(OUT, name + '_x3.png'))
