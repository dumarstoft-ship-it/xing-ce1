"""Brute-force verification of PD-C logic picks. Each check enumerates every model consistent with the stem
and evaluates each option as required by the question form. Prints the option set that satisfies the ask."""
from itertools import permutations, product, combinations
R = {}

def report(qid, models, opts, mode):
    """mode: 'must' (true in all models), 'can' (true in some), 'cannot' (false in all), 'mustnot'(not necessarily true)"""
    res = {}
    for k, f in opts.items():
        vals = [bool(f(m)) for m in models]
        res[k] = (all(vals), any(vals))
    if mode == 'must': ans = [k for k, (a, s) in res.items() if a]
    elif mode == 'can': ans = [k for k, (a, s) in res.items() if s]
    elif mode == 'cannot': ans = [k for k, (a, s) in res.items() if not s]
    elif mode == 'notmust': ans = [k for k, (a, s) in res.items() if not a]
    R[qid] = ans
    print(f'{qid}: models={len(models)} mode={mode} -> {ans}   detail={ {k: ("ALL" if a else ("SOME" if s else "NONE")) for k, (a, s) in res.items()} }')
    return ans

# ---------------- conditions ----------------
def imp(a, b): return (not a) or b

# GD2026-51: 集约->减少; (减少 and 缓慢)->不负面.  Options are conditionals; "必然" = true in all models.
def gd2026_51():
    M = [dict(j=j, d=d, s=s, neg=n) for j, d, s, n in product([0, 1], repeat=4)
         if imp(j, d) and imp(d and s, not n)]
    # option A: not d -> not j ; B: not j -> not d ; C: d -> j ; D: (d and not s) -> neg
    opts = {'A': lambda m: imp(not m['d'], not m['j']), 'B': lambda m: imp(not m['j'], not m['d']),
            'C': lambda m: imp(m['d'], m['j']), 'D': lambda m: imp(m['d'] and not m['s'], m['neg'])}
    report('GD2026-51', M, opts, 'must')

# GD2024-51: not禁止->枯竭; 枯竭->终结; 保障->良性循环
def gd2024_51():
    M = [dict(ban=b, dep=d, end=e, inc=i, good=g) for b, d, e, i, g in product([0, 1], repeat=5)
         if imp(not b, d) and imp(d, e) and imp(i, g)]
    opts = {'A': lambda m: imp(not m['dep'], m['inc']), 'B': lambda m: imp(m['ban'], m['inc']),
            'C': lambda m: imp(not m['end'], m['ban']), 'D': lambda m: imp(not m['inc'], not m['good'])}
    report('GD2024-51', M, opts, 'must')

# GD2022X-59: (羽 and 体) -> 登 ; options about individuals
def gd2022x_59():
    M = [dict(b=b, t=t, c=c) for b, t, c in product([0, 1], repeat=3) if imp(b and t, c)]
    opts = {'A': lambda m: imp(m['b'] and m['c'], m['t']), 'B': lambda m: imp(m['t'] and m['c'], m['b']),
            'C': lambda m: imp((not m['b']) and (not m['c']), not m['t']), 'D': lambda m: imp(m['b'] and not m['c'], not m['t'])}
    report('GD2022X-59', M, opts, 'must')

# GD2022X-57: ¬名->¬言->¬事->¬礼->¬刑->民无措
def gd2022x_57():
    M = [dict(ming=a, yan=b, shi=c, li=d, xing=e, wu=f) for a, b, c, d, e, f in product([0, 1], repeat=6)
         if imp(not a, not b) and imp(not b, not c) and imp(not c, not d) and imp(not d, not e) and imp(not e, f)]
    st = {1: lambda m: imp(m['ming'], m['yan']), 2: lambda m: imp(m['li'], m['shi']), 3: lambda m: imp(not m['ming'], m['wu']),
          4: lambda m: imp(m['shi'], m['ming'] and m['yan'])}
    nec = [k for k, f in st.items() if all(f(m) for m in M)]
    print('GD2022X-57 necessary statements:', nec, '-> option with exactly these: C=234' if nec == [2, 3, 4] else '')
    R['GD2022X-57'] = nec

# GK2023F-114: 稳进 -> 稳主体 ; 渡难关 -> 减税 ; 营商好 -> (减税 and 放管服)?  text: "除了减税降费外，还需继续深化放管服改革，才能营造..."
# => 营商 -> (减税 and 放管服) ; 内生动力 -> 营商 ; 内生动力 -> 三力 ("从而进一步增强" = 内生动力 leads to 三力; treated as 内生->三力)
def gk2023f_114():
    M = []
    for wj, wz, dn, js, fg, ys, ns, sl in product([0, 1], repeat=8):
        if imp(wj, wz) and imp(dn, js) and imp(ys, js and fg) and imp(ns, ys) and imp(ns, sl):
            M.append(dict(wj=wj, wz=wz, dn=dn, js=js, fg=fg, ys=ys, ns=ns, sl=sl))
    opts = {'A': lambda m: imp(m['dn'], m['js']),            # 减税 是 渡难关 的必要条件
            'B': lambda m: imp(m['wz'], m['wj']), 'C': lambda m: imp(m['fg'], m['ys']), 'D': lambda m: imp(not m['ns'], not m['sl'])}
    report('GK2023F-114', M, opts, 'must')

# GK2025F-113
def gk2025f_113():
    M = []
    for gen, tx, gz, sc, ld, xl, kf, zf in product([0, 1], repeat=8):
        # 根基 -> (体系 and 规则); 体系 -> 改革; 改革 -> (流动 and 效率) ; 规则 -> (开放 and 执法)
        gz_rule = gz  # 规则环境
        if imp(gen, tx and gz_rule) and imp(tx, sc) and imp(sc, ld and xl) and imp(gz_rule, kf and zf):
            M.append(dict(gen=gen, tx=tx, gz=gz, sc=sc, ld=ld, xl=xl, kf=kf, zf=zf))
    opts = {'A': lambda m: imp(m['sc'], m['tx']), 'B': lambda m: imp(m['zf'], m['kf']),
            'C': lambda m: imp(m['gz'], m['ld'] and m['xl']),
            'D': lambda m: imp(not (m['kf'] and m['zf']), not m['gen'])}
    report('GK2025F-113', M, opts, 'must')

# GK2020F-108
def gk2020f_108():
    M = []
    for xj, tl, kn, tc, ty, yd, sj in product([0, 1], repeat=7):
        if imp(xj, tl and kn) and imp(tl or tc, ty) and imp(ty, yd) and imp(yd, sj) and not sj:
            M.append(dict(xj=xj, tl=tl, kn=kn, tc=tc))
    opts = {'A': lambda m: not m['xj'], 'B': lambda m: m['kn'], 'C': lambda m: m['tc'], 'D': lambda m: m['tl']}
    report('GK2020F-108', M, opts, 'must')

# GD2026-54: 4 venues 科文博美, not all four; (1) not(文 and 博); (2) 美 or 文; (3) not 美. Which supplement makes 科 certain?
def gd2026_54():
    base = [dict(k=k, w=w, b=b, m=mm) for k, w, b, mm in product([0, 1], repeat=4)
            if not (k and w and b and mm) and not (w and b) and (mm or w) and not mm]
    sup = {'A': lambda m: imp(not m['k'], m['b']), 'B': lambda m: imp(m['b'], not m['k']),
           'C': lambda m: imp(not m['k'], not m['b']), 'D': lambda m: imp(m['b'], not m['k'])}
    ok = []
    for key, f in sup.items():
        mods = [m for m in base if f(m)]
        if mods and all(m['k'] for m in mods): ok.append(key)
    print('GD2026-54 base models', base, '-> supplements forcing 科技馆:', ok); R['GD2026-54'] = ok

# GD2017-53
def gd2017_53():
    M = []
    for a, b in product([0, 1], repeat=2):
        s = [a or b, not a, a, b]
        if sum(map(bool, s)) == 2: M.append(dict(a=a, b=b))
    opts = {'A': lambda m: m['a'] and not m['b'], 'B': lambda m: m['b'] and not m['a'], 'C': lambda m: m['a'] and m['b'], 'D': lambda m: not m['a'] and not m['b']}
    report('GD2017-53', M, opts, 'must')

# GD2022X-61
def gd2022x_61():
    M = []
    for d, b in product([0, 1], repeat=2):
        s = [d and b, (d + b) == 1, not d, b]
        if sum(map(bool, s)) == 1: M.append(dict(d=d, b=b))
    opts = {'A': lambda m: m['d'], 'B': lambda m: not m['d'], 'C': lambda m: m['b'], 'D': lambda m: not m['b']}
    report('GD2022X-61', M, opts, 'must')

# GD2020X-56: one region; exactly one opinion matches
def gd2020x_56():
    M = []
    for r in ['东', '西', '北']:
        adopt = {'甲': r == '东', '乙': r != '北', '丙': r in ('西', '北')}
        if sum(adopt.values()) == 1: M.append(dict(r=r, **adopt))
    opts = {'A': lambda m: m['r'] == '东', 'B': lambda m: m['r'] == '西', 'C': lambda m: m['乙'], 'D': lambda m: m['丙']}
    report('GD2020X-56', M, opts, 'must')

# GD2023X-73 quantifiers: enumerate small populations of typed individuals
def gd2023x_73():
    # attributes: cadre(1)/worker(0), phd, stats, male. Constraints: exists >=2 cadre phd; exists phd & not stats; male -> stats.
    types = [t for t in product([0, 1], repeat=4) if imp(t[3], t[2])]   # (cadre, phd, stats, male)
    M = []
    for k in range(1, 5):
        for pop in combinations(types, k):  # sets of present types (presence is what matters for existential claims)
            if sum(1 for t in pop if t[0] and t[1]) >= 1 and any(t[1] and not t[2] for t in pop):
                M.append(pop)
    opts = {'A': lambda p: any(t[3] and not t[1] for t in p), 'B': lambda p: any(t[1] and not t[3] for t in p),
            'C': lambda p: any(t[3] and not t[0] for t in p), 'D': lambda p: any(t[0] and not t[2] for t in p)}
    report('GD2023X-73', M, opts, 'must')

# GD2020X-67: students choose phys xor hist, and 2 of {政,地,化,生}. Most chem -> phys ; 政 -> 历.
def gd2020x_67():
    stypes = []
    for ph in (0, 1):
        for two in combinations(['政', '地', '化', '生'], 2):
            stypes.append((ph, frozenset(two)))
    stypes = [t for t in stypes if imp('政' in t[1], t[0] == 0)]
    M = []
    # populations: choose counts 0..2 for each type is huge; presence+majority: use counts in {0,1,2,3}
    chem = [t for t in stypes if '化' in t[1]]
    other = [t for t in stypes if '化' not in t[1]]
    # enumerate presence sets of other types (existential only) and counts for chem types to test 'majority'
    for oc in range(0, len(other) + 1):
        for pres in combinations(other, oc):
            for cnt in product(range(0, 4), repeat=len(chem)):
                tot = sum(cnt)
                if tot == 0: continue
                phys = sum(c for c, t in zip(cnt, chem) if t[0] == 1)
                if phys * 2 <= tot: continue
                pop = list(pres) + [t for c, t in zip(cnt, chem) if c > 0]
                M.append(pop)
    st = {'I': lambda p: any('化' in t[1] and '政' in t[1] for t in p), 'II': lambda p: not any('化' in t[1] and '政' in t[1] for t in p),
          'III': lambda p: any('化' in t[1] and '政' not in t[1] for t in p), 'IV': lambda p: any('政' in t[1] and '化' not in t[1] for t in p)}
    nec = [k for k, f in st.items() if all(f(p) for p in M)]
    print('GD2020X-67 necessary:', nec); R['GD2020X-67'] = nec

# GK2022F-109
def gk2022f_109():
    M = []
    for c, l, u in product([0, 1], repeat=3):
        s = [c and l, (c + l) <= 1, c and not l, (not c) and l, imp(c, u)]
        if sum(map(bool, s)) == 1: M.append(dict(c=c, l=l, u=u))
    opts = {'A': lambda m: not m['c'] and not m['l'], 'B': lambda m: m['c'] and m['u'], 'C': lambda m: not m['l'] and not m['u'], 'D': lambda m: m['c'] and m['l']}
    report('GK2022F-109', M, opts, 'must')

# GK2025F-110: 4 people clockwise 甲乙丙丁 around a square table, faces E,S,W,N; exactly one tells truth.
def gk2025f_110():
    dirs_cw = ['北', '东', '南', '西']  # clockwise order viewed from above
    M = []
    for start in range(4):
        seat = {p: dirs_cw[(start + i) % 4] for i, p in enumerate(['甲', '乙', '丙', '丁'])}
        who = {v: k for k, v in seat.items()}
        for truth in ['甲', '乙', '丙', '丁']:
            T = {p: (p == truth) for p in seat}
            st = {'甲': not T[who['东']], '乙': not T[who['南']], '丙': seat['丙'] in ('西', '北'), '丁': seat['丁'] == '北'}
            if all(st[p] == T[p] for p in seat): M.append(dict(seat=seat, truth=truth))
    opts = {'A': lambda m: m['seat']['甲'] == '北', 'B': lambda m: m['seat']['甲'] == '东', 'C': lambda m: m['seat']['乙'] == '西', 'D': lambda m: m['seat']['乙'] == '南'}
    print('   GK2025F-110 models:', M)
    report('GK2025F-110', M, opts, 'must')

# ---------------- combination ----------------
def gd2021z_63():
    M = []
    for vil in permutations(['甲', '乙', '丙']):
        for maj in permutations(['农', '法', '工']):
            P = dict(zip(['蒋', '陈', '刘'], zip(vil, maj)))
            if P['陈'][0] == '甲': continue
            if any(m == '农' and v == '甲' for v, m in P.values()): continue
            if not any(m == '工' and v == '丙' for v, m in P.values()): continue
            if P['陈'][1] == '农': continue
            M.append(P)
    opts = {'A': lambda P: P['刘'][0] == '甲', 'B': lambda P: P['蒋'][0] == '乙', 'C': lambda P: P['刘'][1] == '工', 'D': lambda P: P['陈'][1] == '工'}
    report('GD2021Z-63', M, opts, 'must')

def gd2019x_49():
    roles = ['教硕', '教学', '哲硕', '哲学']
    M = []
    for p in permutations(roles):
        P = dict(zip(['甲', '乙', '丙', '丁'], p))
        if P['甲'] in ('教硕', '哲学'): continue
        if P['甲'][0] != P['丙'][0]: continue
        if P['乙'][1] != '学': continue
        if P['丁'][0] == '哲': continue
        M.append(P)
    opts = {'A': lambda P: P['甲'] == '教学', 'B': lambda P: P['乙'] == '哲学', 'C': lambda P: P['丙'] == '哲学', 'D': lambda P: P['丁'] == '教学'}
    report('GD2019X-49', M, opts, 'must')

def gd2025_59():
    # ranks 1..4 distinct; friendship is a symmetric relation among 4 people (unknown except constraints)
    people = ['甲', '乙', '丙', '丁']
    pairs = list(combinations(people, 2))
    M = []
    for rk in permutations([1, 2, 3, 4]):
        r = dict(zip(people, rk)); by = {v: k for k, v in r.items()}
        for fr in product([0, 1], repeat=len(pairs)):
            F = {frozenset(p) for p, f in zip(pairs, fr) if f}
            third = by[3]; first = by[1]
            if third == '甲' or frozenset(('甲', third)) not in F or not r['甲'] < 3: continue
            if frozenset(('丁', '甲')) in F: continue
            if first == '丁' or frozenset(('丁', first)) not in F: continue
            if not r['乙'] < r['丙']: continue
            M.append(dict(r=r, F=F))
    opts = {'A': lambda m: m['r']['丙'] >= 3, 'B': lambda m: m['r']['甲'] < m['r']['丙'], 'C': lambda m: frozenset(('乙', '丁')) in m['F'],
            'D': lambda m: m['r']['乙'] != 1}
    # ask: which judgement is WRONG -> option that is not necessarily true (ideally false in all)
    res = {k: (all(f(m) for m in M), any(f(m) for m in M)) for k, f in opts.items()}
    print('GD2025-59 models', len(M), {k: ('ALL' if a else ('SOME' if s else 'NONE')) for k, (a, s) in res.items()},
          'ranks seen:', sorted({tuple(m['r'][p] for p in people) for m in M}))
    R['GD2025-59'] = [k for k, (a, s) in res.items() if not a]

def gd2024_58():
    inst = ['钢', '提', '二', '古']
    M = []
    for sets in product(list(combinations(inst, 2)), repeat=4):
        P = dict(zip(['甲', '乙', '丙', '丁'], [set(s) for s in sets]))
        if any(sum(i in s for s in P.values()) != 2 for i in inst): continue
        if '钢' in P['甲']: continue
        if '古' in P['丁']: continue
        if '钢' in P['丙'] or '提' in P['丙']: continue
        if len(P['乙'] & P['丙']) != 1: continue
        M.append(P)
    opts = {'A': lambda P: '提' in P['甲'], 'B': lambda P: '二' not in P['甲'], 'C': lambda P: '古' in P['乙'], 'D': lambda P: not (P['甲'] & P['丁'])}
    print('   GD2024-58 models:', M)
    report('GD2024-58', M, opts, 'must')

def gd2017_51():
    # 6 months; each of 4 people wins in exactly 3 months
    months = range(6)
    subsets = list(combinations(months, 3))
    M = []
    for A in subsets:
        for B in subsets:
            if len(set(A) & set(B)) != 2: continue
            for C in subsets:
                if len(set(B) & set(C)) != 2: continue
                for D in subsets:
                    if set(A) & set(D): continue
                    cnt = [sum(m in S for S in (A, B, C, D)) for m in months]
                    M.append(cnt)
    def k(c, n): return sum(1 for x in c if x == n)
    opts = {'A': lambda c: k(c, 3) == 2, 'B': lambda c: k(c, 2) == 3, 'C': lambda c: k(c, 1) == 1, 'D': lambda c: k(c, 2) < k(c, 1)}
    print('   GD2017-51 count profiles:', sorted({tuple(sorted(c)) for c in M}))
    report('GD2017-51', M, opts, 'must')

def gd2025_53():
    boys = ['赵', '钱', '孙']; girls = ['李', '刘', '王', '吴']
    M = []
    for b in combinations(boys, 2):
        for g in combinations(girls, 2):
            S = set(b) | set(g)
            if ('刘' in S or '吴' in S) and '孙' not in S: continue
            M.append(S)
    opts = {'A': lambda S: '赵' in S or '李' in S, 'B': lambda S: '孙' in S or '王' in S, 'C': lambda S: '钱' in S or '王' in S, 'D': lambda S: '孙' in S or '刘' in S}
    report('GD2025-53', M, opts, 'must')

def gk2023f_115():
    ev = ['单板', '跳台', '越野', '高山']
    ppl = ['石', '方', '白', '于', '叶']
    M = []
    for a in product(ev, repeat=5):
        P = dict(zip(ppl, a))
        cnt = [list(a).count(e) for e in ev]
        if any(c < 1 or c > 2 for c in cnt): continue
        if (P['石'] == '高山' or P['白'] == '高山') and not (P['方'] == '单板' and P['于'] == '高山'): continue
        if (P['于'] == '高山' or P['方'] == '高山') and not (P['白'] == '单板' and P['叶'] == '单板'): continue
        if P['叶'] == '高山': continue
        M.append(P)
    opts = {'A': lambda P: P['方'] == '越野', 'B': lambda P: P['叶'] != '单板', 'C': lambda P: P['石'] == '高山', 'D': lambda P: P['白'] != '跳台'}
    report('GK2023F-115', M, opts, 'must')

def gk2018f_115():
    # 5 chairs labelled 1..5 placed around a round table in unknown order; people sit one per chair.
    # "X坐在k号座椅右边第二张座椅上". Need a convention for left/right around a round table (people face the centre).
    ppl = ['甲', '乙', '丙', '丁', '戊']
    out = {}
    for conv in ('right=+1', 'right=-1'):
        d = 1 if conv == 'right=+1' else -1
        M = []
        for lab in permutations([1, 2, 3, 4, 5]):  # lab[pos] label of chair at circular position pos
            pos_of = {l: i for i, l in enumerate(lab)}
            for sit in permutations(ppl):          # sit[pos] person at position pos
                who_at = {i: p for i, p in enumerate(sit)}
                person_pos = {p: i for i, p in enumerate(sit)}
                person_lab = {p: lab[i] for p, i in person_pos.items()}
                # 均未按顺序坐 -> nobody sits on the chair with his own index (甲1 乙2 丙3 丁4 戊5)
                if any(person_lab[p] == k + 1 for k, p in enumerate(ppl)): continue
                if person_pos['甲'] != (pos_of[1] + 2 * d) % 5: continue
                if person_pos['乙'] != (pos_of[5] - 2 * d) % 5: continue
                if person_pos['丙'] != (pos_of[3] - 1 * d) % 5: continue
                if person_pos['丁'] != (pos_of[2] - 1 * d) % 5: continue
                if person_lab['丙'] != 1: continue
                M.append(person_lab['甲'])
        out[conv] = sorted(set(M))
    print('GK2018F-115 甲 chair label by convention:', out)

def gd2026_62(extra=None, label='GD2026-62'):
    bu = ['教育', '住建', '交通', '农业', '人社', '财政']
    M = []
    for p in permutations(range(1, 7)):  # position from left 1..6
        P = dict(zip(bu, p))
        if P['财政'] != P['人社'] + 1: continue          # 财政 right-adjacent to 人社 (right = larger index from left)
        if not P['住建'] >= P['财政'] + 2: continue       # 财政 left of 住建, not adjacent
        if abs(P['教育'] - P['交通']) != 2: continue
        if extra and not extra(P): continue
        M.append(P)
    return M

if __name__ == '__main__':
    for f in [gd2026_51, gd2024_51, gd2022x_59, gd2022x_57, gk2023f_114, gk2025f_113, gk2020f_108, gd2026_54, gd2017_53, gd2022x_61,
              gd2020x_56, gd2023x_73, gd2020x_67, gk2022f_109, gk2025f_110, gd2021z_63, gd2019x_49, gd2025_59, gd2024_58, gd2017_51,
              gd2025_53, gk2023f_115, gk2018f_115]:
        f()
    base = gd2026_62()
    print('GD2026-62 base models (no extra):', len(base))
    M = gd2026_62(lambda P: abs(P['农业'] - P['财政']) == 1)
    for m in M: print('   ', sorted(m, key=m.get))
    opts = {'A': lambda P: 7 - P['教育'] == 3, 'B': lambda P: 7 - P['住建'] == 2, 'C': lambda P: P['交通'] == 3, 'D': lambda P: P['人社'] == 2}
    report('GD2026-62', M, opts, 'must')
    # mirrored convention: 'right' = smaller index from left
    def mirrored(extra=None):
        bu = ['教育', '住建', '交通', '农业', '人社', '财政']; out = []
        for p in permutations(range(1, 7)):
            P = dict(zip(bu, p))
            if P['财政'] != P['人社'] - 1: continue
            if not P['住建'] <= P['财政'] - 2: continue
            if abs(P['教育'] - P['交通']) != 2: continue
            if extra and not extra(P): continue
            out.append(P)
        return out
    M2 = mirrored(lambda P: abs(P['农业'] - P['财政']) == 1)
    report('GD2026-62(mirror)', M2, opts, 'must')
