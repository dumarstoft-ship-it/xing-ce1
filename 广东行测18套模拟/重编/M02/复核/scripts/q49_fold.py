"""Q49: fold each net and compare the resulting cubes up to rotation.
Glyph readings (from the pixel dumps of s17_p12_i02.png):
  '7' faces: 'up' = direction the glyph's top (its bar) points to, in net terms N/E/S/W;
             chirality 'p' = proper 7, 'm' = mirror image.
  '3' faces: 'bump' = direction the two bulges point to (upright 3 -> E).  A 3 is
             (nearly) symmetric about its bump axis, so only this direction matters.
Net coordinates: (row, col), row grows southwards.
"""
import itertools
import numpy as np

nets = {
    'A': {(0, 0): ('3', 'S'), (0, 1): ('7', 'N', 'p'), (1, 1): ('3', 'S'), (1, 2): ('7', 'W', 'p'),
          (1, 3): ('blank',), (2, 2): ('blank',)},
    'B': {(0, 3): ('3', 'W'), (1, 0): ('blank',), (1, 1): ('blank',), (1, 2): ('3', 'W'),
          (1, 3): ('7', 'E', 'p'), (2, 1): ('7', 'E', 'p')},
    'C': {(0, 2): ('3', 'W'), (0, 3): ('blank',), (1, 0): ('blank',), (1, 1): ('3', 'W'),
          (1, 2): ('7', 'E', 'p'), (2, 1): ('7', 'S', 'm')},   # (2,1): bar at bottom, stem rises from the bar's RIGHT end -> mirrored
    'D': {(0, 2): ('7', 'E', 'p'), (0, 3): ('3', 'N'), (1, 1): ('blank',), (1, 2): ('7', 'W', 'p'),
          (2, 0): ('blank',), (2, 1): ('3', 'S')},
}

def fold(net):
    cells = list(net)
    root = cells[0]
    frames = {root: (np.array([0, 0, 1]), np.array([1, 0, 0]), np.array([0, -1, 0]))}  # n, E, S
    todo = [root]
    while todo:
        c = todo.pop()
        n, E, S = frames[c]
        r, q = c
        for (dr, dq, nf) in [(0, 1, lambda n, E, S: (E, -n, S)), (0, -1, lambda n, E, S: (-E, n, S)),
                             (1, 0, lambda n, E, S: (S, E, -n)), (-1, 0, lambda n, E, S: (-S, E, n))]:
            nb = (r + dr, q + dq)
            if nb in net and nb not in frames:
                frames[nb] = nf(n, E, S)
                todo.append(nb)
    assert len(frames) == 6, 'not connected'
    normals = [tuple(frames[c][0]) for c in cells]
    assert len(set(normals)) == 6, 'overlapping faces - not a cube net'
    faces = {}
    for c in cells:
        n, E, S = frames[c]
        g = net[c]
        dirmap = {'N': -S, 'S': S, 'E': E, 'W': -E}
        if g[0] == 'blank':
            faces[tuple(n)] = ('blank', None, None)
        elif g[0] == '3':
            faces[tuple(n)] = ('3', tuple(dirmap[g[1]]), None)
        else:
            # handedness of a proper 7 on the outside of the face: store (up, chirality)
            faces[tuple(n)] = ('7', tuple(dirmap[g[1]]), g[2])
    return faces

def rotations():
    mats = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product([1, -1], repeat=3):
            M = np.zeros((3, 3), int)
            for i, (p, s) in enumerate(zip(perm, signs)):
                M[i, p] = s
            if round(np.linalg.det(M)) == 1:
                mats.append(M)
    return mats

def same_cube(f1, f2):
    for M in rotations():
        ok = True
        for n, (lab, d, ch) in f1.items():
            n2 = tuple(M @ np.array(n))
            lab2, d2, ch2 = f2[n2]
            if lab2 != lab:
                ok = False; break
            if lab == '3':
                # bump axis direction must agree exactly (symmetric about the bump axis)
                if tuple(M @ np.array(d)) != d2:
                    ok = False; break
            if lab == '7':
                if tuple(M @ np.array(d)) != d2 or ch != ch2:
                    ok = False; break
        if ok:
            return True
    return False

def describe(f):
    out = []
    for n, (lab, d, ch) in sorted(f.items()):
        out.append(f'{n}:{lab}{"" if d is None else d}{"" if ch is None else ch}')
    return ' '.join(out)

folded = {k: fold(v) for k, v in nets.items()}
for k, f in folded.items():
    print(k, describe(f))
print()
for a, b in itertools.combinations(folded, 2):
    print(a, b, 'same cube' if same_cube(folded[a], folded[b]) else 'different')

# C with its bottom 7 read as a proper 7 in every possible orientation (to see whether C
# would be consistent apart from the mirror issue)
print()
for up in 'NESW':
    netC = dict(nets['C']); netC[(2, 1)] = ('7', up, 'p')
    fC = fold(netC)
    print('C if (2,1) were a proper 7 with up=%s:' % up, {k: same_cube(fC, folded[k]) for k in 'ABD'})
