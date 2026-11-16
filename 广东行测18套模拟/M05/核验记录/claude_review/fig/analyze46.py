# Q46: locate hexagon, then strip hexagon outline and label remaining components (circle / triangle / segment)
import numpy as np
from PIL import Image
from collections import deque
im = np.array(Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s19_p12_i00.png').convert('L')).astype(int)
topx = [9, 106, 203, 300, 398, 495, 592]
botx = [105, 202, 300, 397, 495]
cells = {}
for i in range(5):
    cells['F%d' % (i+1)] = (topx[i]+3, 10, topx[i+1]-2, 105)
for i, L in enumerate('ABCD'):
    cells[L] = (botx[i]+3, 137, botx[i+1]-2, 231)

def label(mask):
    H, W = mask.shape
    lab = np.zeros((H, W), int); n = 0; comps = []
    for y in range(H):
        for x in range(W):
            if mask[y, x] and not lab[y, x]:
                n += 1; q = deque([(y, x)]); lab[y, x] = n; pts = []
                while q:
                    cy, cx = q.popleft(); pts.append((cy, cx))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy+dy, cx+dx
                            if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not lab[ny, nx]:
                                lab[ny, nx] = n; q.append((ny, nx))
                comps.append(np.array(pts))
    return comps

def seg_dist(p, a, b):
    p = np.asarray(p, float); a = np.asarray(a, float); b = np.asarray(b, float)
    ab = b - a; t = np.clip(((p - a) @ ab) / (ab @ ab), 0, 1)
    proj = a + np.outer(t, ab) if p.ndim > 1 else a + t * ab
    return np.linalg.norm(p - proj, axis=-1)

for name, (x0, y0, x1, y1) in cells.items():
    sub = im[y0:y1, x0:x1]
    dark = sub < 140
    ys, xs = np.nonzero(dark)
    xmin, xmax, ymin, ymax = xs.min(), xs.max(), ys.min(), ys.max()
    # regular flat-top hexagon from bbox
    cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2
    w = xmax - xmin
    V = [(xmin + w/4, ymin), (xmax - w/4, ymin), (xmax, cy), (xmax - w/4, ymax), (xmin + w/4, ymax), (xmin, cy)]  # V1..V6 clockwise from top-left
    pts = np.stack([xs, ys], 1).astype(float)
    dmin = np.full(len(pts), 1e9)
    for k in range(6):
        dmin = np.minimum(dmin, seg_dist(pts, V[k], V[(k+1) % 6]))
    inner = np.zeros_like(dark)
    keep = dmin > 2.6
    inner[ys[keep], xs[keep]] = True
    comps = [c for c in label(inner) if len(c) >= 6]
    print('==', name, 'hex bbox x[%d,%d] y[%d,%d] center (%.1f,%.1f) side~%.1f' % (xmin, xmax, ymin, ymax, cx, cy, w/2))
    for c in comps:
        cy_, cx_ = c[:, 0].mean(), c[:, 1].mean()
        bx0, bx1, by0, by1 = c[:, 1].min(), c[:, 1].max(), c[:, 0].min(), c[:, 0].max()
        # angle of centroid around hex center (math convention, y up)
        ang = np.degrees(np.arctan2(-(cy_ - cy), cx_ - cx))
        # principal orientation
        cc = c[:, ::-1].astype(float); cc -= cc.mean(0)
        u, s, vt = np.linalg.svd(cc, full_matrices=False)
        d = vt[0]; ori = np.degrees(np.arctan2(-d[1], d[0])) % 180
        elong = s[0] / max(s[1], 1e-6)
        print('   comp n=%3d centroid(%.1f,%.1f) bbox x[%d,%d] y[%d,%d] polar ang=%.0f r=%.1f orient=%.0f elong=%.1f' % (
            len(c), cx_, cy_, bx0, bx1, by0, by1, ang, np.hypot(cx_-cx, cy_-cy), ori, elong))
