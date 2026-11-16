"""Q48: model the hidden '?' region from the visible geometry and compare it with
each option under 0/90/180/270 degree rotations (no flips).
Geometry (from pixel measurements of s17_p12_i01.png):
  outer square x 66..327, y 8..269, 4x4 tiles of 65.25 px;
  quarter disks of radius 1 tile centred at corners / edge midpoints
  (left-mid disk: upper quarter black, lower quarter gray);
  central circle centre (196.5,138.5) r=65.25, inscribed diamond, H/V diameters,
  and segments from each diamond-edge midpoint to the centre.
  '?' box: x 119..171, y 152..204.
"""
import sys
import numpy as np
from PIL import Image, ImageDraw

SRC = sys.argv[1] if len(sys.argv) > 1 else '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s17_p12_i01.png'
S = 8  # supersampling
x0, y0, T = 66.0, 8.0, 65.25

def P(tx, ty):
    return ((x0 + tx * T) * S, (y0 + ty * T) * S)

W, H = 400 * S, 280 * S
img = Image.new('L', (W, H), 255)
d = ImageDraw.Draw(img)
GRAY, BLACK = 190, 0
# quarter disks: (centre, quadrant-angle-range, colour) ; PIL angles: 0=east, clockwise
quarters = [((0, 0), (0, 90), GRAY), ((4, 0), (90, 180), BLACK), ((4, 4), (180, 270), GRAY), ((0, 4), (270, 360), BLACK),
            ((2, 0), (90, 180), BLACK), ((2, 0), (0, 90), GRAY),
            ((4, 2), (180, 270), GRAY), ((4, 2), (90, 180), BLACK),
            ((2, 4), (180, 270), GRAY), ((2, 4), (270, 360), BLACK),
            ((0, 2), (270, 360), BLACK), ((0, 2), (0, 90), GRAY)]
for (cx, cy), (a0, a1), col in quarters:
    px, py = P(cx, cy)
    r = T * S
    d.pieslice([px - r, py - r, px + r, py + r], a0, a1, fill=col, outline=0, width=2 * S)
lw = int(1.5 * S)
cx, cy = P(2, 2)
r = T * S
d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=0, width=lw)
dia = [P(1, 2), P(2, 1), P(3, 2), P(2, 3), P(1, 2)]
d.line(dia, fill=0, width=lw)
d.line([P(1, 2), P(3, 2)], fill=0, width=lw)
d.line([P(2, 1), P(2, 3)], fill=0, width=lw)
for m in [(1.5, 1.5), (2.5, 1.5), (2.5, 2.5), (1.5, 2.5)]:
    d.line([P(*m), P(2, 2)], fill=0, width=lw)
model = img.resize((400, 280), Image.LANCZOS)

src = np.array(Image.open(SRC).convert('L')).astype(float)
box = (121, 154, 170, 203)            # interior of the '?' box
exp = np.array(model.crop(box)).astype(float)
opts = {'A': (30, 312, 77, 358), 'B': (129, 312, 176, 358), 'C': (225, 312, 274, 358), 'D': (322, 312, 371, 358)}  # interiors (borders excluded)

def norm(a):
    a = a - a.mean()
    return a / (np.linalg.norm(a) + 1e-9)

model.save(sys.argv[2]) if len(sys.argv) > 2 else None
# sanity: model vs visible picture outside the box (should correlate strongly)
vis = (66, 8, 327, 269)
m_all = np.array(model.crop(vis)).astype(float)
s_all = src[vis[1]:vis[3], vis[0]:vis[2]].copy()
mask = np.ones_like(s_all, bool)
mask[152 - 8:205 - 8, 119 - 66:172 - 66] = False
print('model vs visible figure (outside ? box) corr = %.3f' % np.corrcoef(m_all[mask], s_all[mask])[0, 1])
from PIL import ImageFilter
expb = np.array(Image.fromarray(exp.astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(float)
def best_shift(a, b, m=3):
    # max correlation over small integer shifts of a against b (central region only)
    best = -1
    h, w = b.shape
    for dy in range(-m, m + 1):
        for dx in range(-m, m + 1):
            aa = np.roll(np.roll(a, dy, 0), dx, 1)[m:h - m, m:w - m]
            bb = b[m:h - m, m:w - m]
            best = max(best, float((norm(aa) * norm(bb)).sum()))
    return best
for k, b in opts.items():
    o = Image.fromarray(src[b[1]:b[3], b[0]:b[2]].astype(np.uint8)).resize(exp.shape[::-1], Image.LANCZOS)
    scores = []
    for rot in (0, 90, 180, 270):
        # PIL rotate is counter-clockwise; report clockwise angle
        r_ = np.array(o.rotate(-rot).filter(ImageFilter.GaussianBlur(1.2))).astype(float)
        scores.append('cw%3d: %.3f' % (rot, best_shift(r_, expb)))
    print(k, ' | '.join(scores))

# focused test: the corner triangle cut off by the diamond edge (top-right of the box after
# rotation) holds the short segment from the centre-to-midpoint line; compare only there.
h, w = exp.shape
yy, xx = np.mgrid[0:h, 0:w]
u, v = xx / (w - 1), yy / (h - 1)
corner = (u > 0.5) & (v < 0.5) & (v < u - 0.5 - 0.06)   # strictly above the diamond edge line
def dark_frac(a):
    return a[corner] < 128
e_dark = dark_frac(exp)
print('corner pixels:', corner.sum(), 'expected dark pixels there:', int(e_dark.sum()))
for k, b in opts.items():
    o = Image.fromarray(src[b[1]:b[3], b[0]:b[2]].astype(np.uint8)).resize(exp.shape[::-1], Image.LANCZOS)
    r_ = np.array(o.rotate(-90)).astype(float)
    o_dark = dark_frac(r_)
    inter = int((o_dark & e_dark).sum()); union = int((o_dark | e_dark).sum())
    print(k, 'cw 90 corner-region dark pixels:', int(o_dark.sum()), ' IoU with expected: %.2f' % (inter / max(union, 1)))
