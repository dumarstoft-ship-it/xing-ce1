"""For each panel: list enclosed white regions (area, approx polygon vertex count).
Polygon approx: dilate region mask to line centre, trace outer boundary, Douglas-Peucker.
usage: python3 polysides.py IMG eps x0,y0,x1,y1 ..."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

def trace_boundary(mask):
    # Moore-neighbour tracing of the outer boundary of a single blob
    ys, xs = np.nonzero(mask)
    start = (ys.min(), xs[ys == ys.min()].min())
    nb = [(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1)]
    H, W = mask.shape
    def inside(p):
        return 0 <= p[0] < H and 0 <= p[1] < W and mask[p]
    b = start; c_dir = 6  # came from west
    pts = [b]
    for _ in range(20000):
        found = False
        for k in range(8):
            d = (c_dir + 1 + k) % 8  # search clockwise starting after backtrack
            p = (b[0] + nb[d][0], b[1] + nb[d][1])
            if inside(p):
                c_dir = (d + 4) % 8
                b = p
                found = True
                break
        if not found:
            break
        if b == start and len(pts) > 2:
            break
        pts.append(b)
    return np.array(pts, dtype=float)

def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    a, b = pts[0], pts[-1]
    ab = b - a
    n = np.hypot(*ab)
    if n == 0:
        d = np.hypot(*(pts - a).T)
    else:
        d = np.abs(ab[0]*(pts[:,1]-a[1]) - ab[1]*(pts[:,0]-a[0])) / n
    i = int(np.argmax(d))
    if d[i] > eps:
        l = rdp(pts[:i+1], eps); r = rdp(pts[i:], eps)
        return np.vstack([l[:-1], r])
    return np.vstack([a, b])

def closed_rdp(pts, eps):
    # split closed contour at the farthest point pair for stability
    i0 = 0
    d = np.hypot(*(pts - pts[i0]).T)
    i1 = int(np.argmax(d))
    p1 = rdp(pts[i0:i1+1], eps)
    p2 = rdp(np.vstack([pts[i1:], pts[:1]]), eps)
    poly = np.vstack([p1[:-1], p2[:-1]])
    # merge nearly collinear consecutive vertices (closed)
    changed = True
    while changed and len(poly) > 3:
        changed = False
        for k in range(len(poly)):
            a, b, c = poly[k-1], poly[k], poly[(k+1) % len(poly)]
            ac = c - a; n = np.hypot(*ac)
            dist = abs(ac[0]*(b[1]-a[1]) - ac[1]*(b[0]-a[0])) / n if n else 0
            if dist < eps:
                poly = np.delete(poly, k, axis=0); changed = True; break
    return poly

def regions(arr, thr=160, min_area=8):
    dark = arr < thr
    lab, n = ndimage.label(~dark)
    border = set(np.unique(np.concatenate([lab[0,:], lab[-1,:], lab[:,0], lab[:,-1]]))) - {0}
    out = []
    for i in range(1, n+1):
        if i in border: continue
        m = lab == i
        if m.sum() < min_area: continue
        out.append(m)
    return out

if __name__ == '__main__':
    img = np.array(Image.open(sys.argv[1]).convert('L'))
    eps = float(sys.argv[2])
    for box in sys.argv[3:]:
        x0, y0, x1, y1 = map(int, box.split(','))
        sub = img[y0:y1, x0:x1]
        res = []
        for m in regions(sub):
            md = ndimage.binary_dilation(m, iterations=1)
            pts = trace_boundary(md)
            poly = closed_rdp(pts, eps)
            cy, cx = ndimage.center_of_mass(m)
            res.append((int(m.sum()), len(poly), (int(cx), int(cy))))
        res.sort(reverse=True)
        print(box, len(res), 'regions;', ' '.join(f'[area {a}, sides {s}, c{c}]' for a, s, c in res))
