"""Q49: exhaustive check whether pieces P1,P2,P3 + option tile the 20-cube target.
Coordinates (x, d, z): x = left->right on the front face, d = depth (away from viewer),
z = height. Read from the oblique drawings (front/top/left faces visible).
All 24 proper rotations are allowed (no mirror images).
"""
import itertools

P1 = {(0,0,0),(0,1,0),(0,2,0),(2,0,0),(2,1,0),(2,2,0),(1,2,0),(1,2,1)}  # U-shape + one on top at back-middle
P2 = {(0,0,1),(1,0,1),(1,0,0),(0,1,1)}                                   # twisted (chiral) tetracube
P3 = {(0,0,0),(1,0,0),(2,0,0),(1,0,1)}                                   # T tetracube
OPTS = {
    "A": {(0,0,0),(1,0,0),(0,1,0),(1,1,0)},                 # 2x2 slab
    "B": {(0,0,0),(0,0,1),(1,0,0),(2,0,0),(1,-1,0)},       # 5 cubes
    "C": {(0,1,0),(1,1,0),(1,0,0)},                         # L-tromino
    "D": {(0,1,0),(1,1,0),(0,2,0),(1,2,0),(1,0,0)},         # P-pentomino
}
TARGET = {(x,d,0) for x in range(3) for d in range(4)} | {(x,d,1) for x in range(2) for d in range(4)}
assert len(TARGET) == 20

def rotations():
    mats = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1,-1), repeat=3):
            m = [[0]*3 for _ in range(3)]
            for i in range(3):
                m[i][perm[i]] = signs[i]
            # determinant
            det = (m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1]) - m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])
                   + m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]))
            if det == 1:
                mats.append(m)
    return mats
ROT = rotations()
assert len(ROT) == 24

def norm(cells):
    mx = min(c[0] for c in cells); my = min(c[1] for c in cells); mz = min(c[2] for c in cells)
    return frozenset((a-mx, b-my, c-mz) for a,b,c in cells)

def orients(piece):
    out = set()
    for m in ROT:
        out.add(norm({tuple(sum(m[i][j]*p[j] for j in range(3)) for i in range(3)) for p in piece}))
    return out

def placements(piece, target):
    res = []
    for o in orients(piece):
        for t in target:
            for anchor in o:
                dx, dy, dz = t[0]-anchor[0], t[1]-anchor[1], t[2]-anchor[2]
                pl = frozenset((a+dx, b+dy, c+dz) for a,b,c in o)
                if pl <= target:
                    res.append(pl)
    return list(set(res))

def solve(pieces, target):
    sols = []
    pls = [placements(p, target) for p in pieces]
    def rec(i, used, chosen):
        if i == len(pieces):
            if used == target:
                sols.append(list(chosen))
            return
        for pl in pls[i]:
            if not (pl & used):
                chosen.append(pl); rec(i+1, used | pl, chosen); chosen.pop()
    rec(0, frozenset(), [])
    return sols

for k, opt in OPTS.items():
    total = len(P1)+len(P2)+len(P3)+len(opt)
    sols = solve([P1, P2, P3, opt], TARGET) if total == 20 else []
    print(f"option {k}: cubes={len(opt)} total={total} tilings={len(sols)}")
    if sols:
        s = sols[0]
        names = ["P1","P2","P3",k]
        for z in (1,0):
            print("  layer z=%d (rows d=3..0, cols x=0..2):" % z)
            for d in range(3,-1,-1):
                row = ""
                for x in range(3):
                    c = (x,d,z)
                    lab = "."
                    for n, pl in zip(names, s):
                        if c in pl: lab = n[-1]
                    row += lab
                print("    ", row)
