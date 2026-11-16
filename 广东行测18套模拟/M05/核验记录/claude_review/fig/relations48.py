# Q48: compare strings by (1) identity pattern, (2) pairwise D4 relations between glyphs
import json, itertools
G = json.load(open('q48_glyphs.json'))
def full(segs):
    s = set(x.split('-')[0] for x in segs)
    # verify both halves present
    for x in list(s):
        h = [y for y in segs if y.startswith(x + '-')]
        assert len(h) == 2, (segs, x)
    return frozenset(s)
glyphs = {k: [full(s) for s in v] for k, v in G.items()}
R90 = {'Ht': 'Vr', 'Vr': 'Hb', 'Hb': 'Vl', 'Vl': 'Ht', 'Hm': 'Vc', 'Vc': 'Hm'}   # rotate 90 deg clockwise
MLR = {'Vl': 'Vr', 'Vr': 'Vl', 'Vc': 'Vc', 'Ht': 'Ht', 'Hm': 'Hm', 'Hb': 'Hb'}   # mirror left-right
def ap(m, g): return frozenset(m[x] for x in g)
def compose(*ms):
    def f(g):
        for m in ms: g = ap(m, g)
        return g
    return f
T = {'id': lambda g: g,
     'r90': compose(R90), 'r180': compose(R90, R90), 'r270': compose(R90, R90, R90),
     'mLR': compose(MLR), 'mTB': compose(MLR, R90, R90), 'mD1': compose(MLR, R90), 'mD2': compose(MLR, R90, R90, R90)}
NAMES = {frozenset({'Ht','Hm','Hb','Vl'}): 'E', frozenset({'Ht','Hm','Hb','Vr'}): 'Ǝ', frozenset({'Ht','Vl','Vc','Vr'}): 'm',
         frozenset({'Hb','Vl','Vc','Vr'}): 'Ш', frozenset({'Ht','Hb','Vl','Vc'}): '[|', frozenset({'Ht','Hb','Vc','Vr'}): '|]',
         frozenset({'Ht','Hm','Vl','Vr'}): 'A', frozenset({'Hm','Hb','Vl','Vr'}): '∀'}
def pattern(seq):
    m = {}; out = ''
    for g in seq:
        if g not in m: m[g] = 'abcdefgh'[len(m)]
        out += m[g]
    return out
def rel(a, b):
    return frozenset(n for n, f in T.items() if f(a) == b)
def relmat(seq):
    return [[rel(seq[i], seq[j]) for j in range(8)] for i in range(8)]
box = glyphs['box']
print('glyph names:')
for k, seq in glyphs.items():
    print('  %-3s' % k, ' '.join(NAMES.get(g, '?') for g in seq), ' identity pattern:', pattern(seq))
# relation comparisons
RB = relmat(box)
for k in 'ABCD':
    RO = relmat(glyphs[k])
    same_pairs = sum(1 for i in range(8) for j in range(i+1, 8) if RB[i][j] == RO[i][j])
    print('option', k, 'pairs with identical D4-relation set as box: %d/28' % same_pairs)
# consecutive relations, rotation-only
def rot_only(a, b):
    return [n for n in ('id', 'r90', 'r180', 'r270') if T[n](a) == b]
for k, seq in glyphs.items():
    print('  %-3s consecutive rotation relations:' % k, [ '/'.join(rot_only(seq[i], seq[i+1])) or '-' for i in range(7)])
    print('       consecutive mirror relations  :', [ '/'.join(n for n in ('mLR','mTB','mD1','mD2') if T[n](seq[i]) == seq[i+1]) or '-' for i in range(7)])
# each glyph's relation to glyph 1
for k, seq in glyphs.items():
    print('  %-3s rel to glyph1 (rotations):' % k, ['/'.join(rot_only(seq[0], g)) or '-' for g in seq])
