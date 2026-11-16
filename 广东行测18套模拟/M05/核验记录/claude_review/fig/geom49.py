# Q49: measure net squares, windows and digit label positions (original pixel coords)
import numpy as np
from PIL import Image
from collections import deque
im = np.array(Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s20_p13_i00.png').convert('L')).astype(int)
dark = im < 128
H, W = dark.shape
def label(mask):
    lab = np.zeros(mask.shape, int); comps = []; n = 0
    for y in range(mask.shape[0]):
        for x in range(mask.shape[1]):
            if mask[y, x] and not lab[y, x]:
                n += 1; q = deque([(y, x)]); lab[y, x] = n; pts = []
                while q:
                    cy, cx = q.popleft(); pts.append((cy, cx))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy+dy, cx+dx
                            if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1] and mask[ny, nx] and not lab[ny, nx]:
                                lab[ny, nx] = n; q.append((ny, nx))
                comps.append(np.array(pts))
    return comps
comps = label(dark)
print('components (bbox x0,x1,y0,y1, n):')
for c in sorted(comps, key=lambda c: (c[:, 1].min(), c[:, 0].min())):
    print('  x[%3d,%3d] y[%3d,%3d] n=%d' % (c[:, 1].min(), c[:, 1].max(), c[:, 0].min(), c[:, 0].max(), len(c)))
# net grid lines (x > 250)
net = dark[:, 250:]
colsum = net.sum(0); rowsum = net.sum(1)
print('net vertical lines (x, count>40):', [(x+250, int(colsum[x])) for x in range(net.shape[1]) if colsum[x] > 40])
print('net horizontal lines (y, count>40):', [(y, int(rowsum[y])) for y in range(H) if rowsum[y] > 40])
