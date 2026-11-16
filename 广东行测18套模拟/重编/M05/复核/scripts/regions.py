"""Count enclosed white regions (faces) inside each panel of a figure-reasoning image.
usage: python3 regions.py <img> x0,y0,x1,y1 [x0,y0,x1,y1 ...]
Each box is a panel interior (inside the panel frame). Prints the bounded faces
(white components not touching the panel border) with area and bbox.
"""
import sys
import numpy as np
from PIL import Image
from collections import deque

def faces(arr, thr=160, min_area=12):
    h, w = arr.shape
    white = arr > thr
    lab = np.zeros((h, w), dtype=np.int32)
    comps = []
    cur = 0
    for y in range(h):
        for x in range(w):
            if white[y, x] and lab[y, x] == 0:
                cur += 1
                q = deque([(y, x)])
                lab[y, x] = cur
                pts = []
                border = False
                while q:
                    cy, cx = q.popleft()
                    pts.append((cy, cx))
                    if cy in (0, h - 1) or cx in (0, w - 1):
                        border = True
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and white[ny, nx] and lab[ny, nx] == 0:
                            lab[ny, nx] = cur
                            q.append((ny, nx))
                if not border and len(pts) >= min_area:
                    ys = [p[0] for p in pts]; xs = [p[1] for p in pts]
                    comps.append(dict(area=len(pts), bbox=(min(xs), min(ys), max(xs), max(ys)),
                                      cx=sum(xs) / len(xs), cy=sum(ys) / len(ys)))
    return comps

if __name__ == "__main__":
    im = Image.open(sys.argv[1]).convert("L")
    arr_full = np.array(im)
    for box in sys.argv[2:]:
        x0, y0, x1, y1 = map(int, box.split(","))
        arr = arr_full[y0:y1, x0:x1]
        fs = faces(arr)
        fs.sort(key=lambda f: -f["area"])
        print(f"panel {box}: {len(fs)} faces")
        for f in fs:
            print("   area=%5d bbox=%s centre=(%.0f,%.0f)" % (f["area"], f["bbox"], f["cx"] + x0, f["cy"] + y0))
