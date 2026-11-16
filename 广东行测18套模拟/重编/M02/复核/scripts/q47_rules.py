"""Q47: feature table read off the nine-grid line figures (see reason in second.json) and
a brute-force test of common row/column rule templates for each candidate option."""
import itertools

# features per figure: lines, strokes, regions, endpoints, junction points, deg>=3 nodes,
# crossings(X), horiz, vert, slant, '/', '\\', graph edges, triangles, max degree, unit-lattice? -
F = {
 '11': dict(L=9, S=5, R=1, E1=6, J=9, D3=5, X=1, H=4, V=5, SL=0, P=0, N=0, ED=15, TRI=0, MD=4),
 '12': dict(L=9, S=3, R=0, E1=4, J=8, D3=2, X=0, H=4, V=5, SL=0, P=0, N=0, ED=11, TRI=0, MD=3),
 '13': dict(L=8, S=3, R=1, E1=3, J=8, D3=3, X=0, H=4, V=4, SL=0, P=0, N=0, ED=11, TRI=0, MD=3),
 '21': dict(L=6, S=3, R=0, E1=4, J=4, D3=2, X=0, H=2, V=3, SL=1, P=0, N=1, ED=7, TRI=0, MD=3),
 '22': dict(L=7, S=4, R=3, E1=4, J=7, D3=6, X=1, H=3, V=2, SL=2, P=0, N=2, ED=13, TRI=1, MD=4),
 '23': dict(L=8, S=1, R=1, E1=1, J=8, D3=1, X=0, H=4, V=3, SL=1, P=1, N=0, ED=9, TRI=0, MD=3),
 '31': dict(L=6, S=1, R=1, E1=2, J=5, D3=1, X=0, H=0, V=2, SL=4, P=2, N=2, ED=7, TRI=1, MD=4),
 '32': dict(L=6, S=2, R=3, E1=1, J=5, D3=3, X=1, H=0, V=2, SL=4, P=2, N=2, ED=8, TRI=3, MD=5),
}
OPT = {
 'A': dict(L=6, S=2, R=1, E1=2, J=5, D3=2, X=0, H=0, V=1, SL=5, P=3, N=2, ED=7, TRI=1, MD=3),
 'B': dict(L=6, S=2, R=1, E1=2, J=5, D3=2, X=0, H=1, V=0, SL=5, P=2, N=3, ED=7, TRI=1, MD=3),
 'C': dict(L=6, S=2, R=2, E1=1, J=5, D3=3, X=0, H=2, V=0, SL=4, P=2, N=2, ED=7, TRI=1, MD=3),
 'D': dict(L=6, S=2, R=2, E1=1, J=5, D3=3, X=0, H=2, V=0, SL=4, P=2, N=2, ED=7, TRI=1, MD=3),
}
feats = list(F['11'].keys())
derived = {}
for a, b in itertools.combinations(feats, 2):
    derived[f'{a}+{b}'] = (lambda d, a=a, b=b: d[a] + d[b])
    derived[f'{a}-{b}'] = (lambda d, a=a, b=b: d[a] - d[b])
for a in feats:
    derived[a] = (lambda d, a=a: d[a])

def grid(fn, opt):
    g = {k: fn(v) for k, v in F.items()}
    g['33'] = fn(OPT[opt])
    return [[g[f'{r}{c}'] for c in '123'] for r in '123']

def rules(m):
    rows = m; cols = [list(c) for c in zip(*m)]
    out = []
    for name, lines in (('row', rows), ('col', cols)):
        if all(l[0] == l[1] == l[2] for l in lines): out.append(f'{name}-constant')
        if all(l[1] - l[0] == l[2] - l[1] != 0 for l in lines): out.append(f'{name}-arith')
        if all(l[0] + l[1] == l[2] for l in lines): out.append(f'{name}-a+b=c')
        if all(l[0] - l[1] == l[2] for l in lines): out.append(f'{name}-a-b=c')
        if len({sum(l) for l in lines}) == 1: out.append(f'{name}-equal-sum')
        s = [sum(l) for l in lines]
        if s[1] - s[0] == s[2] - s[1] != 0: out.append(f'{name}-sum-arith')
        if len({tuple(sorted(l)) for l in lines}) == 1 and len(set(lines[0])) == 3: out.append(f'{name}-same-multiset')
    return out

hits = {}
for fname, fn in derived.items():
    per = {o: rules(grid(fn, o)) for o in OPT}
    for o, rs in per.items():
        for r in rs:
            hits.setdefault((fname, r), set()).add(o)
for (fname, r), os_ in sorted(hits.items()):
    if len(os_) < 4:
        print(f'{fname:8s} {r:22s} -> options {sorted(os_)}')
