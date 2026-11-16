"""Q70: which contour components sit next to each elevation label, and which
components a straight transect crosses (uses q70_labels.npy from q70_contours.py).
Usage: python3 q70_transect.py <dir with q70_labels.npy>"""
import sys

import numpy as np

D = sys.argv[1]
lab = np.load(f"{D}/q70_labels.npy")
ids, counts = np.unique(lab[lab > 0], return_counts=True)
big = set(int(i) for i, c in zip(ids, counts) if c >= 120)

LABELS = {  # label text bbox in original pixels (x0, y0, x1, y1), read off the image
    "1200": (150, 33, 183, 72),
    "1000": (76, 127, 119, 152),
    "900": (327, 124, 361, 143),
    "700": (494, 119, 528, 138),
    "500": (546, 197, 581, 216),
    "400": (549, 271, 584, 288),
}
for name, (x0, y0, x1, y1) in LABELS.items():
    m = 7
    win = lab[max(0, y0 - m):y1 + m, max(0, x0 - m):x1 + m]
    found = sorted(set(int(v) for v in np.unique(win)) & big)
    print(f"label {name}: neighbouring contour components {found}")


def transect(p0, p1, n=2000):
    """record every entry into a contour component from background"""
    seq = []
    prev = 0
    for t in np.linspace(0, 1, n):
        x = int(round(p0[0] + (p1[0] - p0[0]) * t))
        y = int(round(p0[1] + (p1[1] - p0[1]) * t))
        v = int(lab[y, x])
        v = v if v in big else 0
        if v and v != prev:
            seq.append((v, (x, y)))
        prev = v
    return seq


JIA = (140, 83)
HALL = (471, 290)
print("\ntransect 甲 -> hall:")
for v, xy in transect(JIA, HALL):
    print("   ", v, xy)
print("\ntransect 甲 straight down (x=140):")
for v, xy in transect(JIA, (140, 248)):
    print("   ", v, xy)
print("\ntransect hall -> right edge (y=290):")
for v, xy in transect(HALL, (592, 290)):
    print("   ", v, xy)
print("\ntransect hall -> down (x=471):")
for v, xy in transect(HALL, (471, 383)):
    print("   ", v, xy)
print("\ntransect hall -> up (x=471):")
for v, xy in transect(HALL, (471, 6)):
    print("   ", v, xy)
