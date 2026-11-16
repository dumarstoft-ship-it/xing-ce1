"""Q48: boundary matching.

Sector frame: centre O, vertical radius on the left, horizontal radius at the bottom.
  Q sits with its bottom-left corner at O (bottom edge = horizontal radius).
  P sits with its left edge on the vertical radius, top-left corner at the top of it.
  The option, rotated 90 deg clockwise, fills the gap; its straight bottom edge lies on
  the vertical radius directly above Q's left edge.
For a point (X, Y) of the sector frame (X right, Y up, origin O) the option's original
image coordinates are x = BR_x + q_left - Y, y = BR_y - X, where BR is the option's
bottom-right corner and q_left the length of Q's left edge.
We take the cut boundaries of P (everything except its left edge and top arc) and of Q
(its wavy top), map them into every option's frame, and measure the distance from each
mapped point to the option's outline (dark pixels). Small residual = pieces fit.
"""
import numpy as np
from PIL import Image

SRC = "/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s19_p12_i02.png"
im = np.array(Image.open(SRC).convert("L")).astype(float)
dark = im < 128


def centreline_points(x0, y0, x1, y1):
    ys, xs = np.nonzero(dark[y0:y1, x0:x1])
    return np.stack([xs + x0, ys + y0], axis=1).astype(float)


# --- Q: corner and wavy top -----------------------------------------------------------
Qpts = centreline_points(268, 0, 349, 45)
q_bottom_y = np.median(Qpts[Qpts[:, 1] >= Qpts[:, 1].max() - 1][:, 1])     # ~32.5
q_left_x = np.median(Qpts[Qpts[:, 0] <= Qpts[:, 0].min() + 2][:, 0])       # ~274
q_right_x = Qpts[:, 0].max()
# wavy top: for each column strictly inside, mean y of the topmost dark run
top = []
for x in range(int(q_left_x) + 3, int(q_right_x) - 3):
    col = Qpts[(Qpts[:, 0] == x) & (Qpts[:, 1] < q_bottom_y - 4)][:, 1]
    if len(col):
        run = col[col <= col.min() + 3]
        top.append((x, run.mean()))
top = np.array(top)
q_left_len = q_bottom_y - top[0, 1]
Q_cut = np.stack([top[:, 0] - q_left_x, q_bottom_y - top[:, 1]], axis=1)   # (X, Y)
print(f"Q: corner=({q_left_x:.1f},{q_bottom_y:.1f}) bottom length={q_right_x - q_left_x:.1f} "
      f"left edge length~{q_left_len:.1f}")

# --- P: left edge, top-left corner, cut boundary --------------------------------------
Ppts = centreline_points(176, 0, 226, 45)
p_left_x = np.median(Ppts[Ppts[:, 0] <= Ppts[:, 0].min() + 2][:, 0])
p_top_y = Ppts[Ppts[:, 0] <= p_left_x + 1][:, 1].min()
p_left_bottom = Ppts[Ppts[:, 0] <= p_left_x + 1][:, 1].max()
print(f"P: left x={p_left_x:.1f} top y={p_top_y:.1f} left edge bottom y={p_left_bottom:.1f} "
      f"(left edge length {p_left_bottom - p_top_y:.1f})")


def p_cut_points(R):
    """P's outline minus left edge and minus the top arc (points near radius R)"""
    O = np.array([p_left_x, p_top_y + R])
    pts = []
    for x, y in Ppts:
        if x <= p_left_x + 2:
            continue
        r = np.hypot(x - O[0], O[1] - y)
        if abs(r - R) < 2.5:
            continue           # on the arc
        pts.append((x - O[0], O[1] - y))
    return np.array(pts)


def option_outline(x0, x1):
    pts = centreline_points(x0 + 4, 80, x1 - 3, 195)
    by = pts[:, 1].max() - 0.5
    bottom = pts[pts[:, 1] >= by - 1]
    br = np.array([bottom[:, 0].max() - 0.5, by])
    return pts, br


OPTS = dict(zip("ABCD", [(7, 128), (128, 249), (249, 371), (371, 492)]))
for R in (68, 70, 72):
    print(f"--- assumed R = {R}: option straight edge must be R - P_left - Q_left = "
          f"{R - (p_left_bottom - p_top_y) - q_left_len:.1f}")
    Pc = p_cut_points(R)
    for k, (x0, x1) in OPTS.items():
        pts, br = option_outline(x0, x1)

        def to_opt(XY):
            return np.stack([br[0] + q_left_len - XY[:, 1], br[1] - XY[:, 0]], axis=1)

        def resid(XY):
            m = to_opt(XY)
            d = np.sqrt(((m[:, None, :] - pts[None, :, :]) ** 2).sum(-1)).min(1)
            return d.mean(), d.max()

        qa, qm = resid(Q_cut)
        pa, pm = resid(Pc)
        print(f"  option {k}: Q-top vs option right side  mean {qa:.2f} max {qm:.2f} | "
              f"P-cut vs option left side  mean {pa:.2f} max {pm:.2f}")
