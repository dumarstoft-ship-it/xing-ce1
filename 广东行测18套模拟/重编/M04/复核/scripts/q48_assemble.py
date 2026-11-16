"""Q48: can P (small piece) + Q (long strip) + option form a sector?

Hypothesis from inspection: quarter circle, centre O at bottom-left.
  Q : bottom edge = horizontal radius (full length), left edge = lower part of the
      vertical radius, right edge = arc near the horizontal radius, top = wavy cut.
  P : left edge = upper part of the vertical radius, top = arc near the top, bottom = cut.
  option : rotated 90 deg clockwise, its straight bottom edge becomes the middle part of
      the vertical radius; it must fill exactly the region  quarter-disc - P - Q.
The script builds filled masks of every piece, assembles P and Q in the sector frame,
fits R, and scores each rotated option (searching small translations) by IoU with the
remaining region. It also scores the other rotations/mirrors for completeness.
"""
from collections import deque

import numpy as np
from PIL import Image

SRC = "/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s19_p12_i02.png"
im = np.array(Image.open(SRC).convert("L"))
DARK = im < 160


def filled(x0, y0, x1, y1):
    """mask (outline + interior) of the single piece inside the box"""
    sub = DARK[y0:y1, x0:x1]
    h, w = sub.shape
    outside = np.zeros_like(sub, dtype=bool)
    q = deque()
    for y in range(h):
        for x in (0, w - 1):
            if not sub[y, x] and not outside[y, x]:
                outside[y, x] = True
                q.append((y, x))
    for x in range(w):
        for y in (0, h - 1):
            if not sub[y, x] and not outside[y, x]:
                outside[y, x] = True
                q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not sub[ny, nx] and not outside[ny, nx]:
                outside[ny, nx] = True
                q.append((ny, nx))
    m = ~outside
    ys, xs = np.nonzero(m)
    return m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


P = filled(176, 0, 226, 45)
Q = filled(268, 0, 349, 45)
OPTS = {k: filled(x0 + 4, 80, x1 - 3, 195) for k, (x0, x1) in
        zip("ABCD", [(7, 128), (128, 249), (249, 371), (371, 492)])}

print("P mask", P.shape, "area", P.sum())
print("Q mask", Q.shape, "area", Q.sum())
for k, m in OPTS.items():
    print(f"opt {k} mask", m.shape, "area", m.sum())

# --- geometry of P and Q ------------------------------------------------------------
# P: left edge is x=0 column of its mask; top-left corner = (0, 0)
p_left_rows = np.nonzero(P[:, 0])[0]
print("P left edge rows", p_left_rows.min(), p_left_rows.max(), "-> length", p_left_rows.max() - p_left_rows.min())
q_left_rows = np.nonzero(Q[:, 0])[0]
q_bottom_cols = np.nonzero(Q[-1, :])[0]
print("Q left edge rows", q_left_rows.min(), q_left_rows.max(), "length", q_left_rows.max() - q_left_rows.min())
print("Q bottom cols", q_bottom_cols.min(), q_bottom_cols.max(), "length", q_bottom_cols.max() - q_bottom_cols.min())


def outer_profile_top(m):
    """for each column, the first filled row (top boundary)"""
    return np.array([np.nonzero(m[:, x])[0].min() for x in range(m.shape[1])])


# fit R from P's top arc: centre directly below P's top-left corner (outline centre ~1px in)
top = outer_profile_top(P)
best = None
for R in np.arange(55, 80, 0.25):
    # arc: y = R - sqrt(R^2 - x^2) measured from the top line
    xs = np.arange(0, P.shape[1] - 3)
    pred = R - np.sqrt(np.maximum(R ** 2 - xs ** 2, 0))
    err = np.mean((top[xs] - top[0] - pred) ** 2)
    if best is None or err < best[0]:
        best = (err, R)
print(f"R fitted from P's arc: {best[1]:.2f} (mse {best[0]:.2f})")
R_P = best[1]

# fit R from Q's right edge: centre at Q's bottom-left corner
H, W = Q.shape
pts = []
for y in range(H):
    xs_ = np.nonzero(Q[y])[0]
    pts.append((xs_.max(), H - 1 - y))
pts = np.array(pts[2:-2], dtype=float)
r = np.hypot(pts[:, 0], pts[:, 1])
print(f"R from Q's right edge points: mean {r.mean():.2f} sd {r.std():.2f} (min {r.min():.1f} max {r.max():.1f})")
R_Q = r.mean()

# --- assemble in the sector frame -----------------------------------------------------
R = round((R_P + R_Q) / 2)
size = R + 12
canvas_P = np.zeros((size, size), bool)
canvas_Q = np.zeros((size, size), bool)
oy, ox = size - 3, 2          # centre O (row, col) in canvas
# Q: bottom-left corner at O
canvas_Q[oy - H + 1:oy + 1, ox:ox + W] |= Q
# P: top-left corner at height R above O, left edge on the vertical radius
canvas_P[oy - R:oy - R + P.shape[0], ox:ox + P.shape[1]] |= P
yy, xx = np.mgrid[0:size, 0:size]
disc = ((xx - ox) ** 2 + (oy - yy) ** 2 <= R ** 2) & (xx >= ox) & (yy <= oy)
remain = disc & ~canvas_P & ~canvas_Q
print("R used", R, "quarter-disc area", disc.sum(), "P+Q area", (canvas_P | canvas_Q).sum(),
      "remaining", remain.sum())


def score(mask):
    """best IoU of mask placed anywhere near the gap (search translations)"""
    ys, xs = np.nonzero(remain)
    cy, cx = int(ys.mean()), int(xs.mean())
    h, w = mask.shape
    best = (0, None)
    for dy in range(-12, 13):
        for dx in range(-12, 13):
            top_ = cy - h // 2 + dy
            left = cx - w // 2 + dx
            if top_ < 0 or left < 0 or top_ + h > size or left + w > size:
                continue
            cv = np.zeros((size, size), bool)
            cv[top_:top_ + h, left:left + w] = mask
            inter = (cv & remain).sum()
            union = (cv | remain).sum()
            # penalise overlap with P/Q interiors and leaving the disc
            over = (cv & (canvas_P | canvas_Q)).sum()
            outside = (cv & ~disc).sum()
            iou = inter / union
            if iou > best[0]:
                best = (iou, (dy, dx, over, outside))
    return best


TRANSFORMS = {
    "rot90cw": lambda m: np.rot90(m, -1),
    "rot90ccw": lambda m: np.rot90(m, 1),
    "rot180": lambda m: np.rot90(m, 2),
    "id": lambda m: m,
    "mirror+rot90cw": lambda m: np.rot90(m[:, ::-1], -1),
    "mirror+rot90ccw": lambda m: np.rot90(m[:, ::-1], 1),
}
for k, m in OPTS.items():
    res = {t: score(f(m)) for t, f in TRANSFORMS.items()}
    line = "  ".join(f"{t}:{v[0]:.3f}" for t, v in res.items())
    print(f"option {k}: {line}")
    print(f"          best rot90cw detail (dy,dx,overlapPQ,outsideDisc) = {res['rot90cw'][1]}")
