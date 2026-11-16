"""Q47: nine-grid of straight-line figures.

Every figure is drawn on a 3x3 point lattice (coordinates 0,1,2; y grows downward).
Coordinates were read from 6-8x enlargements of
  /home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s23_p12_i01.png
This script computes, for every figure, a set of counting features
(lines, strokes, junction points, closed regions, parallel groups, ...) and then
tests the usual nine-grid rule forms to see which option(s) each feature admits.
"""
from fractions import Fraction as Fr
from itertools import combinations
from collections import defaultdict
import math

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


def P(p):
    return (Fr(p[0]), Fr(p[1]))


def seg_intersections(s, t):
    """Intersection points of two closed segments (assumes no collinear overlap)."""
    (x1, y1), (x2, y2) = map(P, s)
    (x3, y3), (x4, y4) = map(P, t)
    d = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)
    if d == 0:
        return []
    u = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / d
    v = ((x3 - x1) * (y2 - y1) - (y3 - y1) * (x2 - x1)) / d
    if 0 <= u <= 1 and 0 <= v <= 1:
        return [(x1 + u * (x2 - x1), y1 + u * (y2 - y1))]
    return []


def direction(s):
    (x1, y1), (x2, y2) = s
    dx, dy = x2 - x1, y2 - y1
    g = math.gcd(abs(dx), abs(dy))
    dx, dy = dx // g, dy // g
    if dx < 0 or (dx == 0 and dy < 0):
        dx, dy = -dx, -dy
    return (dx, dy)


def kind(s):
    dx, dy = direction(s)
    if dy == 0:
        return 'H'
    if dx == 0:
        return 'V'
    return 'S'


def analyse(segs):
    n = len(segs)
    # points on each segment: endpoints + intersections
    pts_on = [set([P(s[0]), P(s[1])]) for s in segs]
    pair_touch = 0
    for i, j in combinations(range(n), 2):
        ip = seg_intersections(segs[i], segs[j])
        if ip:
            pair_touch += 1
        for p in ip:
            pts_on[i].add(p)
            pts_on[j].add(p)
    # graph
    adj = defaultdict(set)
    edges = set()
    for i, s in enumerate(segs):
        a, b = P(s[0]), P(s[1])
        L = sorted(pts_on[i], key=lambda p: (p[0] - a[0]) ** 2 + (p[1] - a[1]) ** 2)
        for u, v in zip(L, L[1:]):
            e = frozenset((u, v))
            edges.add(e)
            adj[u].add(v)
            adj[v].add(u)
    V = list(adj)
    deg = {v: len(adj[v]) for v in V}
    # components
    seen, comps = set(), 0
    for v in V:
        if v in seen:
            continue
        comps += 1
        stack = [v]
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            stack.extend(adj[x] - seen)
    E = len(edges)
    faces = E - len(V) + comps  # bounded faces (Euler)
    odd = sum(1 for v in V if deg[v] % 2)
    strokes = 0
    # strokes per component: max(1, odd/2)
    seen = set()
    for v in V:
        if v in seen:
            continue
        comp, stack = [], [v]
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            comp.append(x)
            stack.extend(adj[x] - seen)
        o = sum(1 for x in comp if deg[x] % 2)
        strokes += max(1, o // 2)
    junctions = sum(1 for v in V if deg[v] >= 2 and not is_straight_pass(v, adj))
    free_ends = sum(1 for v in V if deg[v] == 1)
    # crossings: points interior to two segments
    def interior(p, s):
        return p != P(s[0]) and p != P(s[1])
    X = T = 0
    for v in V:
        through = sum(1 for s in segs if v in pts_on[segs.index(s)] and interior(v, s))
        ends = sum(1 for s in segs if v in (P(s[0]), P(s[1])))
        if through >= 2:
            X += 1
        elif through == 1 and ends >= 1:
            T += 1
    kinds = [kind(s) for s in segs]
    dirs = defaultdict(int)
    for s in segs:
        dirs[direction(s)] += 1
    par_groups = sum(1 for d, c in dirs.items() if c >= 2)
    par_pairs = sum(c * (c - 1) // 2 for c in dirs.values())
    # right angles: count 90-degree angles between consecutive rays at each vertex
    ra = 0
    for v in V:
        angs = sorted(math.atan2(float(w[1] - v[1]), float(w[0] - v[0])) for w in adj[v])
        if len(angs) < 2:
            continue
        for k in range(len(angs)):
            a1 = angs[k]
            a2 = angs[(k + 1) % len(angs)]
            gap = (a2 - a1) % (2 * math.pi)
            if len(angs) == 2 and k == 1:
                continue
            if abs(gap - math.pi / 2) < 1e-9:
                ra += 1
    lattice = set()
    for s in segs:
        (x1, y1), (x2, y2) = s
        g = math.gcd(abs(x2 - x1), abs(y2 - y1))
        for k in range(g + 1):
            lattice.add((x1 + (x2 - x1) * k // g, y1 + (y2 - y1) * k // g))
    return {
        'lines': n, 'H': kinds.count('H'), 'V': kinds.count('V'), 'S': kinds.count('S'),
        'strokes': strokes, 'odd': odd, 'junctions': junctions, 'free_ends': free_ends,
        'regions': faces, 'parts': comps, 'X': X, 'T': T, 'pair_touch': pair_touch,
        'par_groups': par_groups, 'par_pairs': par_pairs, 'right_angles': ra,
        'lattice_pts': len(lattice), 'edges': E,
    }


def is_straight_pass(v, adj):
    """True if v is just an interior point of one straight line with nothing else (deg 2, collinear)."""
    if len(adj[v]) != 2:
        return False
    a, b = list(adj[v])
    return (a[0] - v[0]) * (b[1] - v[1]) - (a[1] - v[1]) * (b[0] - v[0]) == 0


feat = {k: analyse(v) for k, v in FIG.items()}
names = list(feat['c1'].keys())
print('feature'.ljust(13), ' '.join(k.rjust(3) for k in FIG))
for f in names:
    print(f.ljust(13), ' '.join(str(feat[k][f]).rjust(3) for k in FIG))

grid = ['c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8']
opts = ['A', 'B', 'C', 'D']


def rules(g):
    """g: dict position->value for 9 cells (index 0..8). Yield rule names satisfied."""
    r = [g[0:3], g[3:6], g[6:9]]
    c = [g[0::3], g[1::3], g[2::3]]
    out = []
    if all(len(set(x)) == 1 for x in r): out.append('row-const')
    if all(len(set(x)) == 1 for x in c): out.append('col-const')
    if len(set(g)) == 1: out.append('all-const')
    if all(x[2] - x[1] == x[1] - x[0] for x in r): out.append('row-AP')
    if all(x[2] - x[1] == x[1] - x[0] for x in c): out.append('col-AP')
    if len(set(sum(x) for x in r)) == 1: out.append('row-sum')
    if len(set(sum(x) for x in c)) == 1: out.append('col-sum')
    if all(x[2] == x[0] + x[1] for x in r): out.append('row-add')
    if all(x[2] == abs(x[0] - x[1]) for x in r): out.append('row-diff')
    if all(x[2] == x[0] + x[1] for x in c): out.append('col-add')
    if all(x[2] == abs(x[0] - x[1]) for x in c): out.append('col-diff')
    if all(x[0] == x[2] for x in r): out.append('row-aba')
    if all(x[0] == x[2] for x in c): out.append('col-aba')
    if len(set(tuple(sorted(x)) for x in r)) == 1: out.append('row-perm')
    if len(set(tuple(sorted(x)) for x in c)) == 1: out.append('col-perm')
    d = [g[i + 1] - g[i] for i in range(8)]
    if len(set(d)) == 1: out.append('seq-AP')
    return out


print()
hits = defaultdict(list)
fs = names[:]
# single features and pairwise sums/differences
cands = {f: (lambda k, f=f: feat[k][f]) for f in fs}
for f1, f2 in combinations(fs, 2):
    cands[f1 + '+' + f2] = (lambda k, a=f1, b=f2: feat[k][a] + feat[k][b])
    cands[f1 + '-' + f2] = (lambda k, a=f1, b=f2: feat[k][a] - feat[k][b])
for name, fn in cands.items():
    for o in opts:
        g = [fn(k) for k in grid] + [fn(o)]
        for rname in rules(g):
            hits[(name, rname)].append(o)
unique = {k: v for k, v in hits.items() if len(v) == 1}
print('feature/rule combos admitting exactly one option:')
for (name, rname), v in sorted(unique.items(), key=lambda x: x[0]):
    print(f'  {name:28s} {rname:10s} -> {v[0]}')
print('\nsingle-feature combos admitting 2+ options:')
for (name, rname), v in sorted(hits.items()):
    if len(v) > 1 and '+' not in name and '-' not in name:
        print(f'  {name:28s} {rname:10s} -> {v}')
