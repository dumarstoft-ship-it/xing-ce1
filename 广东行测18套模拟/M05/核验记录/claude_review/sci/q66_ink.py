# Read-only: ink darkness of glyphs in the Q66 y-axis labels (0=black, 255=white).
import numpy as np
from PIL import Image
im = np.array(Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s32_p17_i01.png').convert('L')).astype(int)
def stat(name, box):
    x0, y0, x1, y1 = box
    sub = im[y0:y1 + 1, x0:x1 + 1]
    ink = sub[sub < 200]
    print(f'{name:22s} min={sub.min():3d}  darkest-10%-mean={np.sort(ink)[:max(1,len(ink)//10)].mean():6.1f}  ink-px(<200)={len(ink)}')
stat('digit 2 (2f静max)', (286, 28, 294, 39))
stat('f (2f静max)', (296, 27, 305, 45))
stat('静 (2f静max)', (307, 34, 318, 45))
stat('max (2f静max)', (320, 38, 345, 43))
stat('静 (f静max)', (306, 79, 317, 90))
stat('t1 tick label', (396, 140, 405, 153))
stat('axis label F', (370, 11, 376, 22))
