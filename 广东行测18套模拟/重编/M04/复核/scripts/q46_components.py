"""Q46: measure the short line segment (orientation + position relative to the hexagon
centre) and the circle position in every panel / option via connected components.

Hexagon centre = centre of the bounding box of the largest component (hexagon outline).
Line segment = small elongated component; orientation from PCA.
"""
import math
from collections import deque

import numpy as np
from PIL import Image

SRC = "/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s19_p12_i00.png"
im = np.array(Image.open(SRC).convert("L"))
dark = im < 140

PANELS = {
    "P1": (10, 9, 103, 106), "P2": (107, 9, 200, 106), "P3": (204, 9, 297, 106),
    "P4": (301, 9, 395, 106), "P5": (399, 9, 492, 106),
    "A": (107, 135, 200, 232), "B": (204, 135, 297, 232),
    "C": (301, 135, 395, 232), "D": (399, 135, 492, 232),
}


def components(mask):
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    comps = []
    for y in range(h):
        for x in range(w):
            if mask[y, x] and not seen[y, x]:
                q = deque([(y, x)])
                seen[y, x] = True
                pts = []
                while q:
                    cy, cx = q.popleft()
                    pts.append((cy, cx))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                                seen[ny, nx] = True
                                q.append((ny, nx))
                comps.append(np.array(pts))
    return comps


for name, (x0, y0, x1, y1) in PANELS.items():
    sub = dark[y0:y1, x0:x1]
    comps = sorted(components(sub), key=len, reverse=True)
    hexa = comps[0]
    # hexagon centre from the outline extent (outline = big component)
    cy = (hexa[:, 0].min() + hexa[:, 0].max()) / 2
    cx = (hexa[:, 1].min() + hexa[:, 1].max()) / 2
    out = [f"{name}: centre=({cx + x0:.1f},{cy + y0:.1f})"]
    for c in comps[1:]:
        if len(c) < 8:
            continue
        my, mx = c[:, 0].mean(), c[:, 1].mean()
        cov = np.cov((c[:, 1] - mx), -(c[:, 0] - my))
        evals, evecs = np.linalg.eigh(cov)
        v = evecs[:, 1]
        orient = math.degrees(math.atan2(v[1], v[0])) % 180
        elong = evals[1] / max(evals[0], 1e-6)
        pos = math.degrees(math.atan2(-(my - cy), mx - cx)) % 360
        dist = math.hypot(mx - cx, my - cy)
        kind = "line" if elong > 8 else "blob"
        out.append(f"  {kind}: n={len(c)} centroid=({mx + x0:.1f},{my + y0:.1f}) "
                   f"angle_from_centre={pos:.0f}deg dist={dist:.1f} orient={orient:.0f}deg elong={elong:.1f}")
    print("\n".join(out))
