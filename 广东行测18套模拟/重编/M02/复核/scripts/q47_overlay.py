"""Q47: overlay tests (去同存异 / 求同 / 叠加) on lattice transcriptions of the figures.
Row 1: 4x4 square lattice (unit 24 px).  Row 3: 7-point hexagonal wheel
(B0 top, C0 upper-right, C1 lower-right, B2 bottom, A2 lower-left, A1 upper-left, B1 centre).
Row 2: half-unit lattice in x (18.5 px) and 36 px in y; 2-3 has an off-lattice slant."""
from itertools import product

def unit_edges(segs):
    """split axis/diagonal lattice segments into unit edges"""
    out = set()
    for (x0, y0), (x1, y1) in segs:
        n = max(abs(x1 - x0), abs(y1 - y0))
        dx, dy = (x1 - x0) / n, (y1 - y0) / n
        for k in range(int(n)):
            a = (x0 + dx * k, y0 + dy * k); b = (x0 + dx * (k + 1), y0 + dy * (k + 1))
            out.add(tuple(sorted([a, b])))
    return out

# ---------- row 1 (square lattice) ----------
r11 = unit_edges([((0,0),(3,0)), ((1,0),(1,1)), ((2,0),(2,2)), ((0,1),(3,1)), ((0,2),(0,3)), ((0,3),(1,3)), ((1,2),(1,3)), ((1,2),(3,2)), ((3,2),(3,3))])
r12 = unit_edges([((0,0),(0,1)), ((0,1),(2,1)), ((2,0),(2,1)), ((1,1),(1,3)), ((0,2),(1,2)), ((2,2),(3,2)), ((2,2),(2,3)), ((1,3),(2,3)), ((3,2),(3,3))])
r13 = unit_edges([((0,0),(0,3)), ((0,3),(1,3)), ((1,0),(1,1)), ((1,1),(3,1)), ((3,1),(3,3)), ((2,3),(3,3)), ((2,1),(2,3)), ((0,2),(2,2))])

def sym4(e, n=3):
    # 8 symmetries of the square lattice [0,n]^2
    fs = [lambda x, y: (x, y), lambda x, y: (n - x, y), lambda x, y: (x, n - y), lambda x, y: (n - x, n - y),
          lambda x, y: (y, x), lambda x, y: (n - y, x), lambda x, y: (y, n - x), lambda x, y: (n - y, n - x)]
    return [{tuple(sorted([f(*a), f(*b)])) for a, b in e} for f in fs]

x1 = r11 ^ r12
print('row1: |1-1|=%d |1-2|=%d |1-3|=%d  |1-1 xor 1-2|=%d, common=%d' % (len(r11), len(r12), len(r13), len(x1), len(r11 & r12)))
print('row1: xor == 1-3 under some symmetry?', any(s == r13 for s in sym4(x1)),
      '; best overlap', max(len(s & r13) for s in sym4(x1)))
print('row1: 1-1 or 1-2 == 1-3?', (r11 | r12) == r13, '; and ==', (r11 & r12) == r13)

# ---------- row 3 (hexagonal wheel) ----------
def E(*names):
    return {tuple(sorted(p.split('-'))) for p in names}
r31 = E('A1-B0', 'B0-B1', 'A1-B1', 'B1-C1', 'C0-C1', 'B1-A2', 'A2-B2')
r32 = E('B0-B1', 'B1-B2', 'B0-C0', 'C0-C1', 'C0-B1', 'A1-B1', 'B1-C1', 'C1-B2')
optA = E('A1-B0', 'B0-C0', 'C0-B1', 'B1-A2', 'B1-B2', 'A2-B2', 'B2-C1')
print('row3: 3-1 xor 3-2 =', sorted(r31 ^ r32))
print('row3: option A edges =', sorted(optA), ' equal:', (r31 ^ r32) == optA)
print('row3: common =', sorted(r31 & r32), ' union size', len(r31 | r32))

names8 = ['identity', 'mirror left-right', 'mirror top-bottom', 'rotate 180', 'transpose (mirror about main diagonal)',
          'rotate 90 (y->x)', 'rotate 90 other way', 'anti-transpose']
for nm, s in zip(names8, sym4(x1)):
    if s == r13:
        print('row1: 1-3 =', nm, 'of (1-1 xor 1-2)')

# ---------- row 2 (pixel coordinates inside each cell, read from the dumps) ----------
import math
def segs_close(s, t, tol=5):
    (a, b), (c, d) = s, t
    def dist(p, q): return math.hypot(p[0] - q[0], p[1] - q[1])
    return (dist(a, c) < tol and dist(b, d) < tol) or (dist(a, d) < tol and dist(b, c) < tol)
# 2-1 xor 2-2, worked out on the half-unit lattice x:{13,31,49,67,85}, y:{121,157,193}
xor2 = [((13,121),(49,121)), ((13,121),(13,157)), ((31,121),(31,157)), ((49,121),(49,157)),
        ((49,157),(85,157)), ((85,157),(85,193)), ((49,193),(85,193)), ((31,157),(49,193))]
r23 = [((51,121),(89,121)), ((88,121),(88,157)), ((88,157),(53,173)), ((14,173),(53,173)),
       ((52,121),(52,157)), ((14,157),(52,157)), ((15,157),(15,193)), ((15,193),(52,193))]
def rot(seg, cx, cy, ccw=True):
    out = []
    for (x, y) in seg:
        dx, dy = x - cx, y - cy
        nx, ny = (dy, -dx) if ccw else (-dy, dx)   # screen coords (y down)
        out.append((cx + nx, cy + ny))
    return tuple(out)
for ccw in (True, False):
    rotd = [rot(s, 49, 157, ccw) for s in xor2]
    matched = sum(any(segs_close(r, t) for t in r23) for r in rotd)
    print('row2: (2-1 xor 2-2) rotated 90', 'ccw' if ccw else 'cw', '-> segments matching 2-3: %d/%d' % (matched, len(r23)))

# ---------- row 3: rotate the xor and compare with the four options ----------
import cmath
pointy = {'B0': (0, -1), 'C0': (0.866, -0.5), 'C1': (0.866, 0.5), 'B2': (0, 1), 'A2': (-0.866, 0.5), 'A1': (-0.866, -0.5), 'B1': (0, 0)}
def geom(edges, coords, f=lambda p: p):
    return {tuple(sorted([tuple(round(v, 2) for v in f(coords[a])), tuple(round(v, 2) for v in f(coords[b]))])) for a, b in edges}
xor3 = r31 ^ r32
ccw = lambda p: (p[1], -p[0]); cw = lambda p: (-p[1], p[0])
# options on flat-top hexagon (from the pixel coordinates of each option), centre M
flat = {'R': (1, 0), 'UR': (0.5, -0.866), 'UL': (-0.5, -0.866), 'L': (-1, 0), 'LL': (-0.5, 0.866), 'LR': (0.5, 0.866), 'M': (0, 0)}
optB = [('LL','L'), ('L','UL'), ('UL','M'), ('M','LR'), ('M','R'), ('LR','R'), ('R','UR')]
optC = [('L','UL'), ('UL','UR'), ('UR','R'), ('R','LR'), ('UL','M'), ('M','LR'), ('M','R')]
optD = [('R','UR'), ('UR','UL'), ('UL','L'), ('L','LL'), ('UR','M'), ('M','LL'), ('M','L')]
optA_g = geom(optA, pointy)
cands = {'A': optA_g, 'B': geom(optB, flat), 'C': geom(optC, flat), 'D': geom(optD, flat)}
for nm, f in (('no rotation', lambda p: p), ('rotate 90 ccw', ccw), ('rotate 90 cw', cw)):
    g = geom(xor3, pointy, f)
    print('row3: (3-1 xor 3-2) %-14s equals option:' % nm, [k for k, v in cands.items() if v == g])
