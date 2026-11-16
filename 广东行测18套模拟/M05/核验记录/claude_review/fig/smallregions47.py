# Q47 r3c1 / r3c2 / C : list all enclosed regions with inscribed-circle diameter (px, mm)
import runpy, sys
ns = runpy.run_path('printsize.py', run_name='not_main') if False else None
import numpy as np
from PIL import Image
from collections import deque
S = 0.19609
im = np.array(Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s27_p12_i00.png').convert('L')).astype(int)
cells = {'r3c1': (55, 204, 147, 297), 'r3c2': (154, 204, 247, 297), 'C': (204, 333, 294, 425)}
def comps(mask):
    H, W = mask.shape; lab = np.zeros((H, W), int); out = []; n = 0
    for y in range(H):
        for x in range(W):
            if mask[y, x] and not lab[y, x]:
                n += 1; q = deque([(y, x)]); lab[y, x] = n; pts = []
                while q:
                    cy, cx = q.popleft(); pts.append((cy, cx))
                    for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        ny, nx = cy+dy, cx+dx
                        if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = n; q.append((ny, nx))
                out.append(np.array(pts))
    return out
for name, (x0, y0, x1, y1) in cells.items():
    sub = im[y0:y1, x0:x1]; dk = sub < 160
    H, W = sub.shape; yy, xx = np.mgrid[0:H, 0:W]
    dpts = np.argwhere(dk)
    D = np.sqrt(((yy[..., None] - dpts[:, 0])**2 + (xx[..., None] - dpts[:, 1])**2)).min(-1)
    regs = []
    for c in comps(~dk):
        if c[:, 0].min() == 0 or c[:, 1].min() == 0 or c[:, 0].max() == H-1 or c[:, 1].max() == W-1 or len(c) < 8: continue
        regs.append((len(c), 2 * D[c[:, 0], c[:, 1]].max(), int(c[:, 1].mean()) + x0, int(c[:, 0].mean()) + y0,
                     c[:, 1].max() - c[:, 1].min() + 1, c[:, 0].max() - c[:, 0].min() + 1))
    regs.sort()
    print(name)
    for a, d, cx, cy, w, h in regs:
        print('   area %4dpx (%.2fmm²)  inscribed %.1fpx=%.2fmm  bbox %dx%dpx=%.1fx%.1fmm  at (%d,%d)' % (a, a*S*S, d, d*S, w, h, w*S, h*S, cx, cy))
