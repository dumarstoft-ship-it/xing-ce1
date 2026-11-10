"""Exhaustive check of GD2026-62 and its two PD-C variants (same stem, different added condition / question).
Convention: positions 1..6 counted from the left; '甲在乙的右手边' = larger index (same left-right frame as the options)."""
from itertools import permutations
BU = ['教育', '住建', '交通', '农业', '人社', '财政']

def base_models():
    out = []
    for p in permutations(range(1, 7)):
        P = dict(zip(BU, p))
        if P['财政'] != P['人社'] + 1: continue          # 财政在人社右手边且相邻
        if P['住建'] < P['财政'] + 2: continue           # 财政在住建左手边但不相邻
        if abs(P['教育'] - P['交通']) != 2: continue      # 教育与交通之间隔着一个
        out.append(P)
    return out

def judge(models, opts, mode):
    res = {}
    for k, f in opts.items():
        v = [bool(f(m)) for m in models]
        res[k] = 'ALL' if all(v) else ('SOME' if any(v) else 'NONE')
    if mode == 'must': ans = [k for k, r in res.items() if r == 'ALL']
    elif mode == 'cannot': ans = [k for k, r in res.items() if r == 'NONE']
    elif mode == 'can': ans = [k for k, r in res.items() if r != 'NONE']
    return ans, res

B = base_models()
print('base models', len(B))
for m in B: print('   ', ' '.join(sorted(m, key=m.get)))
fromR = lambda m, d: 7 - m[d]

# original: 农业与财政相邻 -> 必然正确
M0 = [m for m in B if abs(m['农业'] - m['财政']) == 1]
print('ORIG', judge(M0, {'A': lambda m: fromR(m, '教育') == 3, 'B': lambda m: fromR(m, '住建') == 2,
                         'C': lambda m: m['交通'] == 3, 'D': lambda m: m['人社'] == 2}, 'must'))
# V1: 如果住建局在最右端 -> 必然正确
M1 = [m for m in B if m['住建'] == 6]
print('V1', len(M1), judge(M1, {'A': lambda m: m['教育'] == 3, 'B': lambda m: fromR(m, '农业') == 3,
                              'C': lambda m: abs(m['交通'] - m['住建']) == 1, 'D': lambda m: abs(m['农业'] - m['财政']) == 1}, 'must'))
# V2: 无附加条件 -> 不可能为真
print('V2', len(B), judge(B, {'A': lambda m: m['农业'] == 1, 'B': lambda m: m['教育'] == 2,
                            'C': lambda m: m['交通'] == 6, 'D': lambda m: m['住建'] == 4}, 'cannot'))
# robustness: under the mirrored reading of 右手边 the original has no necessarily-true option
def mirror_models():
    out = []
    for p in permutations(range(1, 7)):
        P = dict(zip(BU, p))
        if P['财政'] != P['人社'] - 1: continue
        if P['住建'] > P['财政'] - 2: continue
        if abs(P['教育'] - P['交通']) != 2: continue
        out.append(P)
    return out
MM = mirror_models()
M0m = [m for m in MM if abs(m['农业'] - m['财政']) == 1]
print('ORIG(mirror reading)', judge(M0m, {'A': lambda m: fromR(m, '教育') == 3, 'B': lambda m: fromR(m, '住建') == 2,
                                         'C': lambda m: m['交通'] == 3, 'D': lambda m: m['人社'] == 2}, 'must'))
M1m = [m for m in MM if m['住建'] == 6]
print('V1(mirror reading) models', len(M1m))
print('V2(mirror reading)', judge(MM, {'A': lambda m: m['农业'] == 1, 'B': lambda m: m['教育'] == 2,
                                       'C': lambda m: m['交通'] == 6, 'D': lambda m: m['住建'] == 4}, 'cannot'))
