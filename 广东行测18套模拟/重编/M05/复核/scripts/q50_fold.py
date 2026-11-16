"""Q50: fold the staircase net programmatically and match labelled edges to the cube.
Net cells (col,row), row grows downward:
  S1(0,0) blank | S2(1,0) square
                  S3(1,1) blank | S4(2,1) square
                                  S5(2,2) blank | S6(3,2) square
Net labels: 8 = S1|S2, 5 = S3|S4, 6 = S5|S6, 7 = free top edge of S4.
Cube drawing: square marks on top/front/right; 1=top&back, 2=top&right, 3=bottom&right, 4=front&left.
"""
import itertools
import numpy as np

cells = {"S1": (0,0), "S2": (1,0), "S3": (1,1), "S4": (2,1), "S5": (2,2), "S6": (3,2)}
square = {"S2", "S4", "S6"}

# Fold: each face gets a rigid map net-plane -> 3D.  Start S3 as bottom (z=0) identity.
# Represent map as (R 3x3, t) acting on (x, y, 0) net coordinates (y downward).
def rot_about_axis(p0, axis, ang):
    axis = np.array(axis, float) / np.linalg.norm(axis)
    K = np.array([[0,-axis[2],axis[1]],[axis[2],0,-axis[0]],[-axis[1],axis[0],0]])
    R = np.eye(3) + np.sin(ang)*K + (1-np.cos(ang))*K@K
    return R, np.array(p0, float)

maps = {"S3": (np.eye(3), np.zeros(3))}
adj = []
for a, b in itertools.combinations(cells, 2):
    (ca, ra), (cb, rb) = cells[a], cells[b]
    if abs(ca-cb) + abs(ra-rb) == 1:
        adj.append((a, b))

def apply(m, p):
    R, t = m
    return R @ np.array(p, float) + t

def shared_edge(a, b):
    (ca, ra), (cb, rb) = cells[a], cells[b]
    if ra == rb:
        x = max(ca, cb); return ((x, ra, 0), (x, ra+1, 0))
    y = max(ra, rb); return ((ca, y, 0), (ca+1, y, 0))

# BFS folding: fold child face by +90 deg about the shared edge so it rises toward +z
done = {"S3"}
frontier = ["S3"]
while frontier:
    a = frontier.pop()
    for (p, q) in adj:
        for x, y in ((p, q), (q, p)):
            if x == a and y not in done:
                e0, e1 = shared_edge(x, y)
                # child inherits parent's map, then rotate around the (parent-mapped) edge
                P0, P1 = apply(maps[x], e0), apply(maps[x], e1)
                best = None
                for ang in (np.pi/2, -np.pi/2):
                    R, p0 = rot_about_axis(P0, P1-P0, ang)
                    Rm = R @ maps[x][0]; tm = R @ (maps[x][1] - p0) + p0
                    cy = (cells[y][0]+0.5, cells[y][1]+0.5, 0)
                    c3 = Rm @ np.array(cy) + tm
                    # choose the fold that keeps the child inside the unit cube region
                    inside = all(-1e-6 <= c3[i]-lo <= 1+1e-6 for i, lo in enumerate((1, 1, 0)))
                    if inside: best = (Rm, tm)
                maps[y] = best; done.add(y); frontier.append(y)

def face_normal(f):
    c, r = cells[f]
    cen = apply(maps[f], (c+0.5, r+0.5, 0))
    n = np.round(cen - np.array([1.5, 1.5, 0.5]), 6) * 2
    return tuple(int(v) for v in n)

normals = {f: face_normal(f) for f in cells}
print("folded normals:", normals)

def edge3d(p0, p1, f):
    return frozenset(tuple(np.round(apply(maps[f], p), 6)) for p in (p0, p1))
net_edges = {
    8: edge3d(*shared_edge("S1","S2"), "S1"),
    5: edge3d(*shared_edge("S3","S4"), "S3"),
    6: edge3d(*shared_edge("S5","S6"), "S5"),
    7: edge3d((2,1,0), (3,1,0), "S4"),          # top edge of S4 in the net
}
def faces_of_edge(e):
    pts = [np.array(p) for p in e]
    mid = (pts[0]+pts[1])/2 - np.array([1.5,1.5,0.5])
    return frozenset(f for f, n in normals.items() if abs(np.dot(mid, n) - 0.5) < 1e-6)
net_pairs = {k: faces_of_edge(e) for k, e in net_edges.items()}
print("net edges as face pairs:", {k: sorted(v) for k, v in net_pairs.items()})

# Drawn cube: right=+X, back=+Y, up=+Z
D = {"top": (0,0,1), "bottom": (0,0,-1), "front": (0,-1,0), "back": (0,1,0), "right": (1,0,0), "left": (-1,0,0)}
cube_edges = {1: ("top","back"), 2: ("top","right"), 3: ("bottom","right"), 4: ("front","left")}
drawn_square = {"top","front","right"}

rots = []
for perm in itertools.permutations(range(3)):
    for s in itertools.product((1,-1), repeat=3):
        M = np.zeros((3,3))
        for i in range(3): M[i][perm[i]] = s[i]
        if round(np.linalg.det(M)) == 1: rots.append(M)
inv = {v: k for k, v in D.items()}
results = []
for M in rots:
    img = {f: inv[tuple(int(x) for x in M @ np.array(n))] for f, n in normals.items()}
    if {img[f] for f in square} != drawn_square:
        continue
    mapping = {}
    for k, pair in net_pairs.items():
        names = frozenset(img[f] for f in pair)
        for c, ce in cube_edges.items():
            if names == frozenset(ce): mapping[c] = k
    results.append(mapping)
    print("valid orientation -> cube-edge:net-edge", dict(sorted(mapping.items())))

opts = {"A": {1:7,2:5,3:6,4:8}, "B": {1:6,2:5,3:8,4:7}, "C": {1:5,2:7,3:8,4:6}, "D": {1:5,2:7,3:6,4:8}}
for k, o in opts.items():
    print(f"option {k}: consistent with a valid folding? {any(r == o for r in results)}")
