"""Q50: 18-cube solid (15 white + 3 gray) = piece1 + piece2 + piece3; which option is piece3?

All voxel sets were read from pixel maps of
/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s23_p13_i01.png
(oblique drawing: front faces 16.3 px, depth step (+5, -5.5) px per unit).
Coordinates (x right, y away from viewer, z up) as seen in the FRONT view.
The back view was checked to equal this solid turned 180 degrees about the vertical
(x' = 2 - x, y' = 2 - y): front row there shows 3 white, 3 white, then gray + white on
level 3, the gray top faces at (0,1,1)' and (1,0,2)', etc.
"""
from itertools import product

W, G = 'W', 'G'
SOLID = {
    (0,0,0): W, (1,0,0): W, (0,1,0): W, (1,1,0): W, (2,1,0): W, (0,2,0): W, (1,2,0): W, (2,2,0): W,
    (1,0,1): G, (1,1,1): W, (2,1,1): G, (0,2,1): W, (1,2,1): W, (2,2,1): W,
    (1,0,2): W, (1,1,2): W, (1,2,2): G, (0,2,2): W,
}
P1 = {(0,1,0): W, (1,0,0): W, (1,1,0): W, (2,0,0): W, (2,1,0): W, (2,0,1): G, (2,1,1): W}
# piece 2: visible cubes; (0,1,0) is hidden behind (0,0,0) in the drawing
P2_vis = {(0,0,0): W, (0,0,1): W, (0,1,1): G, (1,1,0): W, (1,1,1): W}
P2_variants = {'P2 (5 visible)': P2_vis, 'P2 + hidden (0,1,0)': {**P2_vis, (0,1,0): W}}
OPTS = {
    'A': {(0,0,0): W, (1,0,0): G, (2,0,0): W, (2,0,1): W, (0,1,0): W},
    'B': {(0,0,0): W, (0,0,1): W, (0,1,0): W, (1,1,0): G, (2,1,0): W},   # (0,1,0) hidden but needed to connect
    'C': {(0,0,0): W, (1,0,0): W, (0,1,0): W, (1,1,0): W, (1,1,1): G, (1,1,2): W},
    'D': {(0,1,0): W, (1,1,0): W, (2,1,0): W, (2,0,0): G, (2,1,1): W},
}

assert sum(v == G for v in SOLID.values()) == 3 and len(SOLID) == 18


def rotations():
    """24 proper rotations as functions on (x,y,z)."""
    def rx(p): x, y, z = p; return (x, -z, y)
    def ry(p): x, y, z = p; return (z, y, -x)
    def rz(p): x, y, z = p; return (-y, x, z)
    mats = set()
    out = []
    for a, b, c in product(range(4), repeat=3):
        def f(p, a=a, b=b, c=c):
            for _ in range(a): p = rx(p)
            for _ in range(b): p = ry(p)
            for _ in range(c): p = rz(p)
            return p
        key = (f((1,0,0)), f((0,1,0)), f((0,0,1)))
        if key not in mats:
            mats.add(key)
            out.append(f)
    assert len(out) == 24
    return out


ROTS = rotations()


def placements(piece):
    """All placements (rotation + translation) of piece inside SOLID with matching colours."""
    res = set()
    for f in ROTS:
        rp = {f(p): c for p, c in piece.items()}
        mx = min(p[0] for p in rp); my = min(p[1] for p in rp); mz = min(p[2] for p in rp)
        rp = {(p[0]-mx, p[1]-my, p[2]-mz): c for p, c in rp.items()}
        for dx, dy, dz in product(range(-1, 4), repeat=3):
            sp = {(p[0]+dx, p[1]+dy, p[2]+dz): c for p, c in rp.items()}
            if all(q in SOLID and SOLID[q] == c for q, c in sp.items()):
                res.add(frozenset(sp))
    return res


pl1 = placements(P1)
print('piece1 placements:', len(pl1))
for name2, p2 in P2_variants.items():
    pl2 = placements(p2)
    print(f'{name2}: placements {len(pl2)}')
    for o, opt in OPTS.items():
        plo = placements(opt)
        sols = 0
        for a in pl1:
            for b in pl2:
                if a & b:
                    continue
                for c in plo:
                    if not (a | b) & c and len(a | b | c) == 18:
                        sols += 1
                        rest = c
        print(f'   option {o} ({len(opt)} cubes): {sols} exact tilings', '' if not sols else f'-> piece3 occupies {sorted(rest)}')

# show the unique tiling with option B
pl2 = placements(P2_variants['P2 + hidden (0,1,0)'])
plB = placements(OPTS['B'])
for a in pl1:
    for b in pl2:
        for c in plB:
            if not (a & b) and not ((a | b) & c) and len(a | b | c) == 18:
                for name, s in [('piece1', a), ('piece2', b), ('piece3=B', c)]:
                    print(f'{name:9s}', sorted(s), ' gray:', [p for p in s if SOLID[p] == G])
                print('layers (z=0,1,2), rows y=2..0, cols x=0..2; 1/2/3 = piece number:')
                lab = {p: '1' for p in a} | {p: '2' for p in b} | {p: '3' for p in c}
                for z in range(3):
                    print(f'  z={z}:', ' | '.join(''.join(lab.get((x, y, z), '.') for x in range(3)) for y in (2, 1, 0)))
