"""Q49: section of the polyhedron by the plane through P, Q, R.

Solid reconstructed from the oblique drawing
(/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s23_p13_i00.png);
unit = cube edge, x to the right, y going back, z up, Q at the origin.
Projection check (original pixels): screen = (25.7 + 19.6x + 7.5y, 102.1 - 7.14y - 19.6z)
  front slab      x 0-3, y 0-2, z 0-1   (front face QR..., right face visible at x=3, y 0-1)
  back block      x 0-4, y 2-3, z 0-2   (top face z=2 visible for x 1-4)
  right box       x 3-4, y 1-3, z 0-2   (front face at y=1)
  wedge           x 0-2, y 0-2, 1 <= z <= 1 + y/2  (slope from edge (y0,z1) up to edge (y2,z2);
                  its right side face, a triangle at x=2, is visible)
  small cube      x 0-1, y 2-3, z 2-3
Points: Q=(0,0,0), R=(3,0,0), P=(1,3,3) (top back right corner of the small cube).
"""
import numpy as np

Q, R, P = np.array([0, 0, 0.]), np.array([3, 0, 0.]), np.array([1, 3, 3.])
n = np.cross(R - Q, P - Q)
print('plane normal', n, '-> plane: %+gy %+gz = 0' % (n[1], n[2]))   # z = y


def inside(x, y, z, e=1e-9):
    box = lambda x0, x1, y0, y1, z0, z1: x0 - e <= x <= x1 + e and y0 - e <= y <= y1 + e and z0 - e <= z <= z1 + e
    return (box(0, 3, 0, 2, 0, 1) or box(0, 4, 2, 3, 0, 2) or box(3, 4, 1, 3, 0, 2)
            or (box(0, 2, 0, 2, 1, 2) and z <= 1 + y / 2 + e) or box(0, 1, 2, 3, 2, 3))


# sample cell centres of the plane z = y, in plane coordinates (x, y); 1 x 1 cells
print('section (rows from back/top to front/bottom; # = solid):')
for yc in [2.5, 1.5, 0.5]:
    row = ''
    for xc in [0.5, 1.5, 2.5, 3.5]:
        # a cell counts as solid if its whole interior is solid (check a fine grid)
        pts = [(xc + dx, yc + dy) for dx in np.linspace(-0.45, 0.45, 7) for dy in np.linspace(-0.45, 0.45, 7)]
        full = all(inside(x, y, y) for x, y in pts)
        none = not any(inside(x, y, y) for x, y in pts)
        row += '#' if full else ('.' if none else '?')
    print('   ', row)

# options drawn as unit-cell grids (top row first), read from the option drawings
OPT = {
    'A': ['.#...', '.##.#', '####.'],
    'B': ['#...', '####', '###.'],
    'C': ['#..', '##.', '###'],
    'D': ['#...', '##.#', '###.'],
}
sec = []
for yc in [2.5, 1.5, 0.5]:
    sec.append(''.join('#' if inside(xc, yc, yc) else '.' for xc in [0.5, 1.5, 2.5, 3.5]))
for k, g in OPT.items():
    print(k, 'matches' if [r.ljust(5, '.') for r in g] == [r.ljust(5, '.') for r in sec] else 'no')
