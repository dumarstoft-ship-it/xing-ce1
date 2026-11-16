"""Q50: exact-cover check. Can the four pieces (rotations only, no mirror) fill each
option's shape inside the 3x3x3 space?  Option shapes come from q50_fit.py (render
matching); voxels hidden in the drawing are enumerated both ways."""
import itertools

# pieces, coordinates (x right, y up, z back) read from the drawing
T5 = {(0, 2, 0), (1, 2, 0), (2, 2, 0), (1, 1, 0), (1, 0, 0)}
L4 = {(0, 2, 0), (1, 2, 0), (1, 1, 0), (1, 0, 0)}
P6 = {(0, 0, 0), (1, 0, 0), (2, 0, 0), (2, 1, 0), (2, 0, 1), (2, 1, 1)}
P4_vis = {(0, 0, 0), (0, 1, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)}
P4_hid = (0, 0, 1)   # hidden behind (0,0,0) in the drawing

def rots():
    mats = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1, -1), repeat=3):
            M = [[0] * 3 for _ in range(3)]
            for i, (p, s) in enumerate(zip(perm, signs)):
                M[i][p] = s
            det = (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1]) - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
                   + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
            if det == 1:
                mats.append(M)
    return mats
ROTS = rots()

def norm(cells):
    mx = min(c[0] for c in cells); my = min(c[1] for c in cells); mz = min(c[2] for c in cells)
    return frozenset((x - mx, y - my, z - mz) for x, y, z in cells)

def orientations(piece):
    out = set()
    for M in ROTS:
        out.add(norm({tuple(sum(M[i][j] * c[j] for j in range(3)) for i in range(3)) for c in piece}))
    return out

def placements(piece, target):
    pls = []
    for o in orientations(piece):
        for dx in range(3):
            for dy in range(3):
                for dz in range(3):
                    s = frozenset((x + dx, y + dy, z + dz) for x, y, z in o)
                    if s <= target:
                        pls.append(s)
    return pls

def solve(pieces, target):
    target = frozenset(target)
    if sum(len(p) for p in pieces) != len(target):
        return []
    pl = [placements(p, target) for p in pieces]
    sols = []
    def rec(i, used, chosen):
        if i == len(pieces):
            if used == target:
                sols.append(list(chosen))
            return
        for s in pl[i]:
            if not (s & used):
                rec(i + 1, used | s, chosen + [s])
    rec(0, frozenset(), [])
    return sols

FULL = {(x, y, z) for x in range(3) for y in range(3) for z in range(3)}
options = {
    'A': ({(0,0,0),(0,1,0),(2,0,0),(2,1,0),(2,1,1),(2,2,1)}, [(0,0,2),(0,1,2),(1,0,1),(1,0,2),(1,1,2)]),
    # B: the greedy fit in q50_fit.py wrongly dropped (0,2,1); zoomed comparison (q50_probe-style, see q50_B3 notes)
    # shows a straight unbroken left edge of the top layer, i.e. (0,2,1) is present.
    'B': ({(1,0,0),(2,0,2),(2,1,0),(2,2,0),(2,2,1),(2,2,2)}, [(0,0,1),(0,0,2),(0,1,1),(0,1,2),(1,0,2),(1,1,1),(1,1,2)]),
    'C': ({(0,0,0),(0,1,0),(0,2,0),(0,2,1),(1,0,0),(1,1,0)}, [(0,0,2),(0,1,2),(1,0,2),(1,1,2)]),
    'D': ({(1,0,0),(1,2,0),(2,0,0),(2,0,2),(2,1,2),(2,2,0)}, [(0,0,1),(0,0,2),(0,1,1),(0,1,2),(1,0,2),(1,1,1),(1,1,2)]),
}

print('piece 4 (5 visible cubes) chiral?', orientations(P4_vis) != orientations({(-x, y, z) for x, y, z in P4_vis}))
for p4name, P4 in [('P4 5 cubes', P4_vis), ('P4 6 cubes (hidden cube present)', P4_vis | {P4_hid})]:
    pieces = [T5, L4, P6, P4]
    tot = sum(len(p) for p in pieces)
    print(f'\n== {p4name}: total {tot} cubes')
    for k, (miss, hidden) in options.items():
        base = FULL - miss
        n_all_hidden = len(base)
        results = []
        for r in range(len(hidden) + 1):
            for drop in itertools.combinations(hidden, r):
                tgt = base - set(drop)
                if len(tgt) != tot:
                    continue
                s = solve(pieces, tgt)
                results.append((drop, len(s)))
        ok = [d for d, n in results if n > 0]
        print(f'{k}: drawn shape with every hidden cube present = {n_all_hidden} cubes; '
              f'hidden-cube choices with right count: {len(results)}; solvable choices: {len(ok)}')
        for d in ok[:6]:
            print('     solvable if hidden cubes removed:', d)
