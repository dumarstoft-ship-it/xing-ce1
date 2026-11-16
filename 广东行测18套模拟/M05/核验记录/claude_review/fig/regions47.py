# Q47: count enclosed white regions per cell (flood fill), report region areas
import numpy as np
from PIL import Image
from collections import deque
img = np.array(Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s27_p12_i00.png').convert('L')).astype(int)
xs = [51, 150, 250, 350]; ys = [6, 100, 200, 300]
cells = {}
for r in range(3):
    for c in range(3):
        cells['r%dc%d' % (r+1, c+1)] = (xs[c]+4, ys[r]+4, xs[c+1]-3, ys[r+1]-3)
bx = [6, 103, 200, 297, 394]
for i, L in enumerate('ABCD'):
    cells[L] = (bx[i]+4, 333, bx[i+1]-3, 425)

def comps(mask):
    H, W = mask.shape; lab = np.zeros((H, W), int); out = []; n = 0
    for y in range(H):
        for x in range(W):
            if mask[y, x] and not lab[y, x]:
                n += 1; q = deque([(y, x)]); lab[y, x] = n; cnt = 0; touch = False
                while q:
                    cy, cx = q.popleft(); cnt += 1
                    if cy in (0, H-1) or cx in (0, W-1): touch = True
                    for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        ny, nx = cy+dy, cx+dx
                        if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = n; q.append((ny, nx))
                out.append((cnt, touch))
    return out

for thr in (160, 200):
    print('--- threshold', thr)
    for k, (x0, y0, x1, y1) in cells.items():
        sub = img[y0:y1, x0:x1]
        white = sub >= thr
        cs = comps(white)
        inner = sorted([c for c, t in cs if not t], reverse=True)
        big = [c for c in inner if c >= 8]
        print(k, 'enclosed regions(>=8px):', len(big), 'areas:', big, ' tiny:', [c for c in inner if c < 8])
