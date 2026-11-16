"""Q47 verification: rule = overlay figures 1 and 2 of each row, remove common segments
(去同存异, compared segment by segment on the 3x3 lattice), then rotate the result
90 degrees clockwise -> figure 3.

Lattice coordinates (x right, y down, values 0..2) read from 6-8x enlargements of
/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s23_p12_i01.png
"""
import math
from itertools import product

FIG = {
    'c1': [((0,0),(2,0)), ((2,0),(0,1)), ((0,1),(2,2)), ((0,1),(0,2)), ((0,2),(2,2))],
    'c2': [((0,0),(0,1)), ((0,1),(2,0)), ((0,2),(2,1)), ((2,1),(2,2)), ((0,2),(2,2))],
    'c3': [((0,0),(2,0)), ((2,0),(2,2)), ((0,0),(1,2)), ((1,0),(0,2)), ((0,2),(1,2))],
    'c4': [((0,0),(0,1)), ((0,1),(2,1)), ((1,0),(1,2)), ((1,0),(0,2)), ((0,2),(2,2))],
    'c5': [((0,0),(2,0)), ((0,0),(0,1)), ((1,0),(1,2)), ((2,0),(2,2)), ((1,1),(2,2)), ((0,2),(2,2))],
    'c6': [((0,0),(2,1)), ((1,0),(1,2)), ((2,0),(2,2)), ((0,2),(1,1)), ((0,2),(2,2))],
    'c7': [((0,0),(1,0)), ((0,0),(0,1)), ((0,1),(1,1)), ((1,0),(1,2)), ((1,1),(2,0)),
           ((0,2),(2,1)), ((2,1),(2,2)), ((1,2),(2,2))],
    'c8': [((0,0),(2,1)), ((0,0),(0,1)), ((0,1),(1,1)), ((0,2),(2,1)), ((2,1),(2,2)), ((1,2),(2,2))],
    'A':  [((0,0),(0,1)), ((0,1),(2,1)), ((2,0),(2,1)), ((2,0),(1,2)), ((1,1),(2,2))],
    'B':  [((0,0),(1,0)), ((1,0),(1,2)), ((1,2),(2,2)), ((0,0),(2,1)), ((1,1),(2,0))],
    'C':  [((0,0),(1,0)), ((1,0),(1,2)), ((0,0),(2,1)), ((1,1),(2,0))],
    'D':  [((0,1),(2,1)), ((2,0),(2,1)), ((2,0),(1,2)), ((1,1),(2,2))],
}


def units(name, f=lambda x, y: (x, y)):
    """Set of unit lattice segments of a figure after applying point map f."""
    out = set()
    for (x1, y1), (x2, y2) in FIG[name]:
        g = math.gcd(abs(x2 - x1), abs(y2 - y1))
        pts = [(x1 + (x2 - x1) * k // g, y1 + (y2 - y1) * k // g) for k in range(g + 1)]
        for a, b in zip(pts, pts[1:]):
            out.add(tuple(sorted([f(*a), f(*b)])))
    return frozenset(out)


ROT = {  # screen coordinates, y downward
    'none': lambda x, y: (x, y),
    'cw90': lambda x, y: (2 - y, x),
    '180': lambda x, y: (2 - x, 2 - y),
    'ccw90': lambda x, y: (y, 2 - x),
}


def rotate(segset, f):
    return frozenset(tuple(sorted([f(*a), f(*b)])) for a, b in segset)


for rname, f in ROT.items():
    ok1 = rotate(units('c1') ^ units('c2'), f) == units('c3')
    ok2 = rotate(units('c4') ^ units('c5'), f) == units('c6')
    res = rotate(units('c7') ^ units('c8'), f)
    match = [o for o in 'ABCD' if units(o) == res]
    print(f'xor then rotate {rname:5s}: row1 {ok1}, row2 {ok2}; row3 result matches {match}')

print('\ncommon segments row1:', sorted(units('c1') & units('c2')))
print('common segments row2:', sorted(units('c4') & units('c5')))
print('common segments row3:', sorted(units('c7') & units('c8')))
print('B minus C:', sorted(units('B') - units('C')), '(a segment common to c7 and c8)')
print('A minus D:', sorted(units('A') - units('D')))
