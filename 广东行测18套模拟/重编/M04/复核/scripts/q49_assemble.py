"""Q49: which option is piece 3 such that pieces 1, 2, 3 tile the big polycube?

Coordinates read from 7x enlargements (oblique projection, depth goes up-right):
  x = column (left->right), y = level (bottom->top), z = layer (front=0 -> back).
Big solid: 4 x 3 x 3 box minus column x=3 at z=0 (all levels) and minus (3,2,1)
  (0-based x,y,z) -> 32 cubes, no hidden voids assumed.
Pieces: cells that are visible are fixed; cells that are completely hidden are listed
separately and every subset of them is tried (keeping the piece face-connected).
Only proper rotations (24) are allowed, no mirror images.
"""
import itertools

import numpy as np

BIG = {(x, y, z) for x in range(4) for y in range(3) for z in range(3)}
BIG -= {(3, y, 0) for y in range(3)}
BIG -= {(3, 2, 1)}
assert len(BIG) == 32

# piece 1: columns a,b,c -> x 0..2 ; levels 1..3 -> y 0..2 ; front cube layer 0, rest layer 1
P1_vis = {(0, 0, 1), (0, 1, 1), (1, 1, 1), (2, 0, 1), (2, 1, 1), (2, 2, 1), (1, 0, 0)}
P1_hid = [(1, 0, 1)]
# piece 2: layers 0..2
P2_vis = {(0, 0, 2), (0, 1, 2), (0, 2, 2), (1, 2, 2), (2, 0, 2), (2, 1, 2), (2, 2, 2),
          (1, 2, 1), (2, 0, 1), (2, 1, 1),
          (1, 0, 0), (1, 1, 0)}
P2_hid = [(1, 0, 2), (1, 1, 2), (1, 0, 1), (1, 1, 1)]
# options (layer 2 = back wall, b1 sticks out two layers to the front)
OPT = {
    "A": ({(0, 0, 2), (0, 1, 2), (1, 1, 2), (2, 0, 2), (2, 1, 2), (1, 0, 1), (1, 0, 0)}, [(1, 0, 2)]),
    "B": ({(0, 0, 2), (0, 1, 2), (1, 1, 2), (2, 0, 2), (1, 0, 1), (1, 0, 0)}, [(1, 0, 2)]),
    "C": ({(0, 0, 2), (1, 1, 2), (2, 0, 2), (2, 1, 2), (1, 0, 1), (1, 1, 1), (1, 0, 0)}, [(1, 0, 2)]),
    "D": ({(0, 0, 2), (1, 0, 2), (1, 1, 2), (2, 1, 2), (1, 0, 1), (1, 0, 0)}, []),
}


def connected(cells):
    cells = set(cells)
    if not cells:
        return False
    start = next(iter(cells))
    seen, st = {start}, [start]
    while st:
        x, y, z = st.pop()
        for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            n = (x + d[0], y + d[1], z + d[2])
            if n in cells and n not in seen:
                seen.add(n)
                st.append(n)
    return len(seen) == len(cells)


def variants(vis, hid):
    out = []
    for k in range(len(hid) + 1):
        for sub in itertools.combinations(hid, k):
            s = frozenset(vis | set(sub))
            if connected(s):
                out.append(s)
    return out


def rotations():
    mats = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1, -1), repeat=3):
            m = np.zeros((3, 3), int)
            for i in range(3):
                m[i, perm[i]] = signs[i]
            if round(np.linalg.det(m)) == 1:
                mats.append(m)
    return mats


ROTS = rotations()
assert len(ROTS) == 24


def normalize(cells):
    a = np.array(sorted(cells))
    a = a - a.min(axis=0)
    return frozenset(map(tuple, a))


def all_orients(cells):
    return {normalize([tuple(m @ np.array(c)) for c in cells]) for m in ROTS}


def placements(cells, region):
    """all placements (rotation + translation) of the piece inside region"""
    res = set()
    rx = [c[0] for c in region]
    ry = [c[1] for c in region]
    rz = [c[2] for c in region]
    for o in all_orients(cells):
        mx = max(c[0] for c in o)
        my = max(c[1] for c in o)
        mz = max(c[2] for c in o)
        for dx in range(min(rx), max(rx) - mx + 1):
            for dy in range(min(ry), max(ry) - my + 1):
                for dz in range(min(rz), max(rz) - mz + 1):
                    p = frozenset((c[0] + dx, c[1] + dy, c[2] + dz) for c in o)
                    if p <= region:
                        res.add(p)
    return res


p1_vars = variants(P1_vis, P1_hid)
p2_vars = variants(P2_vis, P2_hid)
print("piece1 sizes", sorted(len(v) for v in p1_vars))
print("piece2 sizes", sorted(len(v) for v in p2_vars))
opt_vars = {k: variants(v, h) for k, (v, h) in OPT.items()}
for k, vs in opt_vars.items():
    print(f"option {k} sizes", sorted(len(v) for v in vs))

found = {k: [] for k in OPT}
for p1 in p1_vars:
    for pl1 in placements(p1, BIG):
        rest1 = BIG - pl1
        for p2 in p2_vars:
            if len(p2) > len(rest1):
                continue
            for pl2 in placements(p2, rest1):
                rest = rest1 - pl2
                if not rest:
                    continue
                shape = all_orients(rest)
                for k, vs in opt_vars.items():
                    for v in vs:
                        if len(v) == len(rest) and normalize(v) in shape:
                            found[k].append((len(p1), len(p2), sorted(pl1), sorted(pl2), sorted(rest)))

for k, sols in found.items():
    print(f"option {k}: {len(sols)} tilings")
    for s in sols[:3]:
        print(f"   |p1|={s[0]} |p2|={s[1]}\n   p1 at {s[2]}\n   p2 at {s[3]}\n   p3 = {s[4]}")
