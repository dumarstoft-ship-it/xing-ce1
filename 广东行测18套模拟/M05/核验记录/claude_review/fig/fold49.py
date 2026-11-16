# Q49: fold the outer-surface net onto a cube, enumerate the 24 proper rotations (and 24 improper for contrast),
# keep those mapping window faces onto the visible windowed faces (top/front/right), and read off edge pairs.
import numpy as np, itertools
# net squares: name -> (col,row) ; window flag  (row index grows downward)
net = {'a': ((0, 0), False), 'b': ((1, 0), True), 'c': ((1, 1), False), 'd': ((2, 1), True), 'e': ((2, 2), False), 'f': ((3, 2), True)}
# labelled net edges: label -> (face, side)   side in E,W,N,S (net directions; N = up on page)
net_labels = {8: ('a', 'E'), 5: ('c', 'E'), 6: ('e', 'E'), 7: ('d', 'N')}
# Folding frame: viewer looks at the net from +z (outer surfaces visible), cube folds behind (-z).
# For each face: n = outward normal, u = net-right direction, v = net-down direction (3D, y up)
X, Y, Z = np.eye(3, dtype=int)
frames = {'c': (Z, X, -Y)}          # root
pos = {k: v[0] for k, v in net.items()}
from collections import deque
q = deque(['c'])
while q:
    f = q.popleft(); n, u, v = frames[f]; (cx, cy) = pos[f]
    for g, (gx, gy) in pos.items():
        if g in frames: continue
        d = (gx - cx, gy - cy)
        if d == (1, 0):   frames[g] = (u, -n, v)
        elif d == (-1, 0): frames[g] = (-u, n, v)
        elif d == (0, 1):  frames[g] = (v, u, -n)
        elif d == (0, -1): frames[g] = (-v, u, n)
        else: continue
        q.append(g)
assert len(frames) == 6
normals = {f: tuple(frames[f][0]) for f in frames}
assert len(set(normals.values())) == 6, normals
def edge_mid(face, side):
    n, u, v = frames[face]
    return tuple({'E': n + u, 'W': n - u, 'N': n - v, 'S': n + v}[side])
print('folded face normals:', {f: normals[f] for f in sorted(normals)})
# check gluing: every net edge midpoint shared by exactly two faces
mids = {}
for f in frames:
    for s in 'EWNS':
        mids.setdefault(edge_mid(f, s), []).append(f + s)
assert len(mids) == 12 and all(len(v) == 2 for v in mids.values())
for lab, (f, s) in net_labels.items():
    m = edge_mid(f, s)
    print('net label %d: %s.%s -> cube edge mid %s, glued pair %s' % (lab, f, s, m, mids[m]))
# Opposite pairs
for f in sorted(frames):
    for g in sorted(frames):
        if f < g and normals[f] == tuple(-np.array(normals[g])): print('opposite:', f, g)
# The solid as drawn: front=+z (faces viewer), top=+y, right=+x, back recedes up-right.
view_windows = {(0, 1, 0), (0, 0, 1), (1, 0, 0)}
view_labels = {1: (0, 1, -1),   # top/back edge
               2: (1, 1, 0),    # top/right edge
               3: (1, -1, 0),   # right/bottom edge
               4: (-1, 0, 1)}   # front/left edge
inv_view = {v: k for k, v in view_labels.items()}
# 48 signed permutation matrices
mats = []
for perm in itertools.permutations(range(3)):
    for signs in itertools.product((1, -1), repeat=3):
        M = np.zeros((3, 3), int)
        for i in range(3): M[i, perm[i]] = signs[i]
        mats.append(M)
assert len(mats) == 48
def describe(M):
    det = round(np.linalg.det(M))
    out = {}
    wins = {tuple(M @ np.array(normals[f])) for f in frames if net[f][1]}
    ok = wins == view_windows
    for lab, (f, s) in net_labels.items():
        m = tuple(M @ np.array(edge_mid(f, s)))
        out[lab] = inv_view.get(m, None)
    return det, ok, out
proper_ok = []; improper_ok = []
for M in mats:
    det, ok, out = describe(M)
    if ok:
        (proper_ok if det == 1 else improper_ok).append((M, out))
print('\nproper rotations (det=+1) mapping net windows onto top/front/right: %d' % len(proper_ok))
for M, out in proper_ok:
    print('  ', M.tolist(), ' net->view:', {k: v for k, v in out.items()})
print('improper (mirror, det=-1) placements mapping windows onto top/front/right: %d' % len(improper_ok))
for M, out in improper_ok:
    print('  ', M.tolist(), ' net->view:', {k: v for k, v in out.items()})
opts = {'A': {1: 7, 2: 5, 3: 6, 4: 8}, 'B': {1: 6, 2: 5, 3: 8, 4: 7}, 'C': {1: 5, 2: 7, 3: 8, 4: 6}, 'D': {1: 5, 2: 7, 3: 6, 4: 8}}
def consistent(opt, out):
    # out: net label -> view label (or None). option says view label i <-> net label j
    return all(out[j] == i for i, j in opt.items())
for name, lst in (('proper', proper_ok), ('improper', improper_ok)):
    print('\n%s:' % name)
    for L, opt in opts.items():
        hits = [i for i, (M, out) in enumerate(lst) if consistent(opt, out)]
        print('  option %s %s consistent with placements %s' % (L, opt, hits))
