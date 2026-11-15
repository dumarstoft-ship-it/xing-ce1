"""Q48: objective symbol identity check on the ORIGINAL figure (s23_p12_i02.png).
Segments the 8 symbols of each row (stem, A-D), then compares every pair of symbols
pixel-wise after centring, both as-is (0 deg) and rotated 180 deg / mirrored.
Purpose: confirm the hand reading 'which end face of the disc is visible' and whether
symbols that look alike are the very same drawing or a 180-degree-rotated copy."""
import numpy as np
from PIL import Image
im = Image.open('/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s23_p12_i02.png').convert('L')
a = np.array(im)
ink = a < 160
rows = {'stem': (12, 60), 'A': (74, 126), 'B': (129, 181), 'C': (184, 236), 'D': (239, 291)}
def label(mask):
    H, W = mask.shape; lab = np.zeros((H, W), int); n = 0
    for y in range(H):
        for x in range(W):
            if mask[y, x] and not lab[y, x]:
                n += 1; st = [(y, x)]; lab[y, x] = n
                while st:
                    cy, cx = st.pop()
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not lab[ny, nx]:
                                lab[ny, nx] = n; st.append((ny, nx))
    return lab, n
symbols = {}
for r, (y0, y1) in rows.items():
    band = ink[y0:y1, 35:395]
    lab, n = label(band)
    comps = []
    for k in range(1, n + 1):
        ys, xs = np.where(lab == k)
        if len(ys) < 60: continue          # dashed-frame dashes, specks
        comps.append((xs.min(), xs.max(), ys.min(), ys.max(), k))
    comps.sort()
    assert len(comps) == 8, (r, len(comps), comps)
    for i, (x0, x1, yy0, yy1, k) in enumerate(comps):
        sub = (lab[yy0:yy1 + 1, x0:x1 + 1] == k)
        g = 255 - a[y0 + yy0:y0 + yy1 + 1, 35 + x0:35 + x1 + 1].astype(float)
        g = g * sub   # keep only this symbol's ink
        symbols[f'{r}{i+1}'] = g
def score(p, q):
    # normalised cross-correlation of two greyscale symbols on a common canvas, best over small shifts
    H = max(p.shape[0], q.shape[0]) + 4; W = max(p.shape[1], q.shape[1]) + 4
    def put(s, dy, dx):
        c = np.zeros((H, W)); oy = (H - s.shape[0]) // 2 + dy; ox = (W - s.shape[1]) // 2 + dx
        c[oy:oy + s.shape[0], ox:ox + s.shape[1]] = s; return c
    P = put(p, 0, 0); best = -1
    for dy in (-2, -1, 0, 1, 2):
        for dx in (-2, -1, 0, 1, 2):
            Q = put(q, dy, dx)
            v = (P * Q).sum() / np.sqrt((P * P).sum() * (Q * Q).sum()); best = max(best, v)
    return best
names = list(symbols)
# reference prototypes from the stem, read by hand: s1=top face visible (U), s2=bottom face (D),
# s4=right face (R), s5='\' tilt face lower-left (LL), s8='/' tilt face upper-left (UL)
protos = {}
hand = {'stem': ['U','D','D','R','LL','U','R','UL'],
        'A': ['LL','L','L','UL','U','LL','UL','U'],
        'B': ['R','U','U','LL','UR','R','LL','LR'],
        'C': ['U','LL','UR','R','LR','U','R','D'],
        'D': ['UR','LL','LL','LR','L','LL','LR','R']}
print('symbol  hand  best-match(as drawn)  corr  | corr with same symbol rotated 180')
for nm in names:
    row = ''.join(ch for ch in nm if not ch.isdigit()); idx = int(''.join(ch for ch in nm if ch.isdigit())) - 1
    best = max(((score(symbols[nm], symbols[o]), o) for o in names if o != nm), key=lambda t: t[0])
    print(f'{nm:7s} {hand[row][idx]:4s} {best[1]:7s} {best[0]:.3f}')
# pairwise check of the contested pairs
pairs = [('C2','C3'), ('B4','B5'), ('B5','B7'), ('D1','D2'), ('stem1','stem2'), ('stem5','B4'), ('stem5','C2'), ('B5','C3'), ('C3','D1')]
for p, q in pairs:
    s0 = score(symbols[p], symbols[q]); s180 = score(symbols[p], np.rot90(symbols[q], 2))
    print(f'{p} vs {q}: as drawn {s0:.3f}; after rotating {q} by 180 deg {s180:.3f}')
np.save('q48_symbols.npy', symbols, allow_pickle=True)
