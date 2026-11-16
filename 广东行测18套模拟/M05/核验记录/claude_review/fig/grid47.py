# Find frame lines of Q47 and crop cells at 5x
import numpy as np, os
from PIL import Image
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crops')
img = Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s27_p12_i00.png').convert('L')
im = np.array(img)
H, W = im.shape
dark = im < 128
rows = dark.sum(1)
print('H,W', H, W)
print('rows >150:', [(i, int(rows[i])) for i in range(H) if rows[i] > 150])
top = dark[:310]; bot = dark[310:]
print('top cols >150:', [(j, int(top[:, j].sum())) for j in range(W) if top[:, j].sum() > 150])
print('bot cols >60:', [(j, int(bot[:, j].sum())) for j in range(W) if bot[:, j].sum() > 60])
