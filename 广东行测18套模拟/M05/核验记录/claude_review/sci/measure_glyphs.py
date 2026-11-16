# Read-only: connected components (8-neighbour) of dark pixels inside label boxes,
# to get individual glyph heights (mm) at source print scale.
import json
from collections import deque
import numpy as np
from PIL import Image
ROOT = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/'
inv = {o['id']: o for o in json.load(open(ROOT + '图片清单.json'))}
PT = 25.4 / 72
def sc(aid):
    x0, y0, x1, y1 = inv[aid]['bbox_pt']
    return (x1 - x0) * PT / inv[aid]['width_px'], (y1 - y0) * PT / inv[aid]['height_px']
def comps(aid, box, thr=150, minpix=3):
    im = np.array(Image.open(ROOT + 'assets/' + aid + '.png').convert('L'))
    x0, y0, x1, y1 = box
    m = im[y0:y1, x0:x1] < thr
    H, W = m.shape
    seen = np.zeros_like(m, bool)
    out = []
    for y in range(H):
        for x in range(W):
            if m[y, x] and not seen[y, x]:
                q = deque([(y, x)]); seen[y, x] = True; pts = []
                while q:
                    cy, cx = q.popleft(); pts.append((cy, cx))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < H and 0 <= nx < W and m[ny, nx] and not seen[ny, nx]:
                                seen[ny, nx] = True; q.append((ny, nx))
                if len(pts) >= minpix:
                    ys = [p[0] for p in pts]; xs = [p[1] for p in pts]
                    out.append((x0 + min(xs), y0 + min(ys), x0 + max(xs), y0 + max(ys), len(pts)))
    out.sort()
    return out
def show(aid, name, box):
    sx, sy = sc(aid)
    print(f'-- {aid} {name} box={box}')
    for c in comps(aid, box):
        w, h = c[2] - c[0] + 1, c[3] - c[1] + 1
        print(f'     comp x{c[0]}-{c[2]} y{c[1]}-{c[3]}  {w}x{h}px = {w*sx:.2f}x{h*sy:.2f} mm  (pix={c[4]})')
# Q66
show('s32_p17_i01', 'label 2f静max', (298, 22, 372, 52))
show('s32_p17_i01', 'label f静max', (298, 62, 372, 94))
show('s32_p17_i01', 'tick labels t1 t2 t3', (385, 128, 485, 161))
show('s32_p17_i01', 'axis-end label t', (565, 100, 600, 132))
show('s32_p17_i01', 'y-axis label F', (366, 5, 390, 28))
# Q67
show('s27_p18_i01', 'label R0', (530, 285, 574, 325))
show('s27_p18_i01', 'label L1', (225, 283, 262, 320))
show('s27_p18_i01', 'label L2', (350, 560, 395, 599))
show('s27_p18_i01', 'A1 inside circle', (95, 365, 150, 412))
show('s27_p18_i01', 'label S', (358, 400, 385, 430))
# Q70
show('s23_p19_i11', '1320 + triangle', (138, 118, 220, 146))
show('s23_p19_i11', 'label 800', (408, 196, 462, 220))
show('s23_p19_i11', 'label 1:300000', (8, 410, 128, 447))
print('==== extra ====')
show('s32_p17_i01', 'label 2f静max incl. digit 2', (270, 20, 300, 52))
show('s32_p17_i01', 'curve stroke at peak column x=425 near y=36', (420, 28, 432, 45))
