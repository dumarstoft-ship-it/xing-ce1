"""第48题：按“摆放方向 + 可见底面(椭圆)所在一侧”给每个圆柱图元分类。
方法：取图元掩膜，按四个候选方向(0°,90°,45°,135°)旋转摆正成“横放”姿态，
再看横放姿态下额外那条椭圆弧在上半还是下半，从而得到可见底面的朝向。"""
from PIL import Image
import numpy as np
from scipy import ndimage

IMG = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s23_p12_i02.png'
im = Image.open(IMG).convert('L')
a = np.array(im) < 150
lab, n = ndimage.label(a)
objs = ndimage.find_objects(lab)
items = []
for i, sl in enumerate(objs):
    ys, xs = sl
    h = ys.stop - ys.start; w = xs.stop - xs.start
    if 15 < h < 60 and 15 < w < 60:
        cy = (ys.start + ys.stop) / 2; cx = (xs.start + xs.stop) / 2
        items.append((cy, cx, sl, i + 1))
rows = {'frame': (0, 60), 'A': (60, 125), 'B': (125, 180), 'C': (180, 240), 'D': (240, 295)}
groups = {}
for k, (y0, y1) in rows.items():
    g = sorted([it for it in items if y0 <= it[0] < y1], key=lambda t: t[1])
    groups[k] = g

def mask(it, pad=12):
    cy, cx, sl, idx = it
    m = (lab[sl] == idx)
    return np.pad(m, pad)

def orient_and_face(m):
    """Return face direction angle in degrees (0=right, 90=up, 180=left, 270=down), image y down.
    Strategy: the glyph is a cylinder outline; the visible face is an ellipse whose 'inner arc' lies
    inside the silhouette. Rotate the glyph by angle t so that the cylinder's long silhouette is
    horizontal (width>height), then look at which half (upper/lower) holds more interior line pixels."""
    best = None
    for t in (0, 45, 90, 135):
        r = ndimage.rotate(m.astype(float), t, reshape=True, order=1) > 0.3
        ys, xs = np.nonzero(r)
        h = ys.max() - ys.min() + 1; w = xs.max() - xs.min() + 1
        score = w / h
        if best is None or score > best[0]:
            best = (score, t, r)
    score, t, r = best
    ys, xs = np.nonzero(r)
    r = r[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    H, W = r.shape
    # interior pixels: exclude outer silhouette boundary by filling and eroding
    filled = ndimage.binary_fill_holes(r)
    inner = r & ndimage.binary_erosion(filled, iterations=3)
    # count interior line pixels in upper vs lower half (central columns only)
    c0, c1 = W // 5, W - W // 5
    up = inner[:H // 2, c0:c1].sum(); lo = inner[H // 2:, c0:c1].sum()
    # in the rotated (upright-horizontal) frame, visible face at top => face dir = 90 deg
    face_in_rot = 90 if up > lo else 270
    # rotating the image by +t (ndimage.rotate is counter-clockwise for positive angle on display)
    # means original direction = rotated direction - t
    face = (face_in_rot - t) % 360
    return t, face, up, lo

names = {0: 'right', 45: 'up-right', 90: 'up', 135: 'up-left', 180: 'left', 225: 'down-left', 270: 'down', 315: 'down-right'}
result = {}
for k, g in groups.items():
    faces = []
    for it in g:
        t, face, up, lo = orient_and_face(mask(it))
        faces.append(face)
    result[k] = faces
    print(k, [names[f] for f in faces])

# pattern of equal elements -> canonical letters
def pattern(seq):
    m = {}; out = ''
    for s in seq:
        if s not in m:
            m[s] = 'abcdefghij'[len(m)]
        out += m[s]
    return out
for k, f in result.items():
    print(k, 'pattern', pattern(f))
