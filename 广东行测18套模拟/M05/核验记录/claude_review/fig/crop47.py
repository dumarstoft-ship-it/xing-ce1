# Crop Q47 cells 5x
import os
from PIL import Image
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crops')
img = Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s27_p12_i00.png').convert('L')
xs = [51, 150, 250, 350]; ys = [6, 100, 200, 300]
for r in range(3):
    for c in range(3):
        box = (xs[c]+1, ys[r]+1, xs[c+1]-1, ys[r+1]-1)
        cc = img.crop(box); cc = cc.resize((cc.size[0]*5, cc.size[1]*5), Image.LANCZOS)
        cc.save(os.path.join(OUT, 'q47_r%dc%d.png' % (r+1, c+1)))
bx = [6, 103, 200, 297, 394]
for i, L in enumerate('ABCD'):
    box = (bx[i]+1, 330, bx[i+1]-1, 427)
    cc = img.crop(box); cc = cc.resize((cc.size[0]*5, cc.size[1]*5), Image.LANCZOS)
    cc.save(os.path.join(OUT, 'q47_%s.png' % L))
big = img.crop((50, 5, 352, 301)).resize((302*3, 296*3), Image.LANCZOS); big.save(os.path.join(OUT, 'q47_grid_x3.png'))
opt = img.crop((5, 327, 396, 430)).resize((391*3, 103*3), Image.LANCZOS); opt.save(os.path.join(OUT, 'q47_opts_x3.png'))
print('ok')
