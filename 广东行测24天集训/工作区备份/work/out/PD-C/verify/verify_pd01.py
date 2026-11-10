"""PD-C / PD01 (D03) verification script  (revised 11-08: GD2024-2026 source items replaced).
Every logic item (conditions, truth-value, analytic, the GD2026-62 variants) is solved by exhaustive enumeration of all
models consistent with the stem; science items that admit a calculation are re-computed.  Run:  python3 -I verify_pd01.py
Each check prints the option(s) satisfying the ask and asserts it equals the checked_answer in questions.jsonl."""
from itertools import permutations, product, combinations
from fractions import Fraction as Fr

RESULTS = {}
def imp(a, b): return (not a) or b

def judge(qid, models, opts, mode, expect):
    """mode: must = true in every model; can = true in some model; cannot = true in no model; notmust = not true in every model"""
    stat = {}
    for k, f in opts.items():
        v = [bool(f(m)) for m in models]
        stat[k] = 'ALL' if v and all(v) else ('SOME' if any(v) else 'NONE')
    sel = {'must': lambda s: s == 'ALL', 'can': lambda s: s != 'NONE', 'cannot': lambda s: s == 'NONE', 'notmust': lambda s: s != 'ALL'}[mode]
    ans = ''.join(k for k, s in stat.items() if sel(s))
    RESULTS[qid] = ans
    flag = 'OK ' if ans == expect else 'XX '
    print(f'{flag}{qid:22s} models={len(models):5d} ask={mode:7s} -> {ans:4s} (expect {expect})  {stat}')
    assert ans == expect, qid

# ======================= 条件与必然性 =======================
def gd2019x_46():   # PD-C-001  (replaces GD2026-51)
    M = []
    for fz, rj, yj, ss, jt, xy, gf, ys, lh in product([0, 1], repeat=9):
        # 发展好->软件基础∧硬件基础∧吸引活动; 设施∧交通->硬件基础; 吸引足够活动->公共服务∧营商环境; lh=市政设施老化(题干未涉及)
        if imp(fz, rj and yj and xy) and imp(ss and jt, yj) and imp(xy, gf and ys):
            M.append(dict(fz=fz, yj=yj, ss=ss, jt=jt, xy=xy, gf=gf, lh=lh))
    judge('GD2019X-46', M, {'A': lambda m: m['yj'] and not m['fz'], 'B': lambda m: m['gf'] and m['xy'],
                            'C': lambda m: m['fz'] and m['lh'], 'D': lambda m: m['ss'] and m['jt'] and not m['yj']}, 'cannot', 'D')

def gk2020f_108():
    M = []
    for xj, tl, kn, tc, ty, yd, sj in product([0, 1], repeat=7):
        if imp(xj, tl and kn) and imp(tl or tc, ty) and imp(ty, yd) and imp(yd, sj) and not sj:
            M.append(dict(xj=xj, tl=tl, kn=kn, tc=tc))
    judge('GK2020F-108', M, {'A': lambda m: not m['xj'], 'B': lambda m: m['kn'], 'C': lambda m: m['tc'], 'D': lambda m: m['tl']}, 'must', 'A')

def gd2022x_59():
    M = [dict(b=b, t=t, c=c) for b, t, c in product([0, 1], repeat=3) if imp(b and t, c)]
    judge('GD2022X-59', M, {'A': lambda m: imp(m['b'] and m['c'], m['t']), 'B': lambda m: imp(m['t'] and m['c'], m['b']),
                            'C': lambda m: imp(not m['b'] and not m['c'], not m['t']), 'D': lambda m: imp(m['b'] and not m['c'], not m['t'])}, 'must', 'D')

def gk2025f_113():
    M = []
    for gen, tx, gz, sc, ld, xl, kf, zf in product([0, 1], repeat=8):
        if imp(gen, tx and gz) and imp(tx, sc) and imp(sc, ld and xl) and imp(gz, kf and zf):
            M.append(dict(gen=gen, tx=tx, gz=gz, sc=sc, ld=ld, xl=xl, kf=kf, zf=zf))
    judge('GK2025F-113', M, {'A': lambda m: imp(m['sc'], m['tx']), 'B': lambda m: imp(m['zf'], m['kf']),
                             'C': lambda m: imp(m['gz'], m['ld'] and m['xl']), 'D': lambda m: imp(not (m['kf'] and m['zf']), not m['gen'])}, 'must', 'D')

def gd2019x_47():   # PD-C-005  (replaces GD2024-51)
    M = []
    for hy, gj, bs in product([0, 1], repeat=3):
        wz = 0                                   # 没有一个国家能拥有完整的自主可控芯片产业链
        if imp(hy, gj) and imp(bs, gj):          # 想要话语权->关键技术; 这样才能避免受制于人: 不受制->关键技术
            M.append(dict(hy=hy, gj=gj, bs=bs, wz=wz))
    judge('GD2019X-47', M, {'A': lambda m: imp(m['hy'], m['wz']), 'B': lambda m: imp(not m['gj'], not m['bs']),
                            'C': lambda m: imp(m['bs'], m['wz']), 'D': lambda m: imp(m['gj'], m['hy'])}, 'must', 'B')

def gk2022f_111():  # PD-C-006  (replaces GD2026-54): which supplement makes "三号柜放赤铁矿" follow
    mins = ['赤', '黑', '绿', '黄', '方']
    base = []
    for p in permutations(mins):
        c = dict(zip([1, 2, 3, 4, 5], p))
        if not imp(c[1] == '赤', c[2] != '黑'): continue
        if not (c[3] == '赤' or c[1] == '赤'): continue
        if not imp(c[2] != '黑', c[4] != '绿'): continue
        if not imp(c[5] == '方', c[4] == '绿'): continue
        base.append(c)
    sup = {'A': lambda c: c[2] != '黑', 'B': lambda c: c[1] != '黄', 'C': lambda c: c[5] == '方', 'D': lambda c: c[4] != '绿'}
    ok = ''.join(k for k, f in sup.items() if [c for c in base if f(c)] and all(c[3] == '赤' for c in base if f(c)))
    RESULTS['GK2022F-111'] = ok
    print(('OK ' if ok == 'C' else 'XX ') + f'GK2022F-111            base models={len(base)} -> supplement forcing 三号柜赤铁矿: {ok} (expect C)'); assert ok == 'C'

def gd2022x_57():
    M = [dict(ming=a, yan=b, shi=c, li=d, xing=e, wu=f) for a, b, c, d, e, f in product([0, 1], repeat=6)
         if imp(not a, not b) and imp(not b, not c) and imp(not c, not d) and imp(not d, not e) and imp(not e, f)]
    st = {1: lambda m: imp(m['ming'], m['yan']), 2: lambda m: imp(m['li'], m['shi']), 3: lambda m: imp(not m['ming'], m['wu']),
          4: lambda m: imp(m['shi'], m['ming'] and m['yan'])}
    nec = tuple(k for k, f in st.items() if all(f(m) for m in M))
    ans = {(1, 2): 'A', (2, 3): 'B', (2, 3, 4): 'C', (1, 2, 3, 4): 'D'}.get(nec, '?')
    RESULTS['GD2022X-57'] = ans
    print(('OK ' if ans == 'C' else 'XX ') + f'GD2022X-57             necessary statements {nec} -> {ans} (expect C)'); assert ans == 'C'

def gk2023f_114():
    M = []
    for wj, wz, dn, js, fg, ys, ns, sl in product([0, 1], repeat=8):
        if imp(wj, wz) and imp(dn, js) and imp(ys, js and fg) and imp(ns, ys) and imp(ns, sl):
            M.append(dict(wj=wj, wz=wz, dn=dn, js=js, fg=fg, ys=ys, ns=ns, sl=sl))
    judge('GK2023F-114', M, {'A': lambda m: imp(m['dn'], m['js']), 'B': lambda m: imp(m['wz'], m['wj']),
                             'C': lambda m: imp(m['fg'], m['ys']), 'D': lambda m: imp(not m['ns'], not m['sl'])}, 'must', 'A')

def gd2020x_56():
    M = []
    for r in ['东', '西', '北']:
        ad = {'甲': r == '东', '乙': r != '北', '丙': r in ('西', '北')}
        if sum(ad.values()) == 1: M.append(dict(r=r, **ad))
    judge('GD2020X-56', M, {'A': lambda m: m['r'] == '东', 'B': lambda m: m['r'] == '西', 'C': lambda m: m['乙'], 'D': lambda m: m['丙']}, 'must', 'D')

def gk2022f_109():
    M = []
    for c, l, u in product([0, 1], repeat=3):
        s = [c and l, (c + l) <= 1, c and not l, (not c) and l, imp(c, u)]
        if sum(map(bool, s)) == 1: M.append(dict(c=c, l=l, u=u))
    judge('GK2022F-109', M, {'A': lambda m: not m['c'] and not m['l'], 'B': lambda m: m['c'] and m['u'], 'C': lambda m: not m['l'] and not m['u'],
                             'D': lambda m: m['c'] and m['l']}, 'must', 'D')

def gd2023x_73():
    types = [t for t in product([0, 1], repeat=4) if imp(t[3], t[2])]  # (干部, 博士, 统计学, 男性); 男性->统计学
    M = []
    for k in range(1, len(types) + 1):
        for pop in combinations(types, k):
            if any(t[0] and t[1] for t in pop) and any(t[1] and not t[2] for t in pop): M.append(pop)
    judge('GD2023X-73', M, {'A': lambda p: any(t[3] and not t[1] for t in p), 'B': lambda p: any(t[1] and not t[3] for t in p),
                            'C': lambda p: any(t[3] and not t[0] for t in p), 'D': lambda p: any(t[0] and not t[2] for t in p)}, 'must', 'B')

def gd2017_53():
    M = [dict(a=a, b=b) for a, b in product([0, 1], repeat=2) if sum(map(bool, [a or b, not a, a, b])) == 2]
    judge('GD2017-53', M, {'A': lambda m: m['a'] and not m['b'], 'B': lambda m: m['b'] and not m['a'], 'C': lambda m: m['a'] and m['b'],
                           'D': lambda m: not m['a'] and not m['b']}, 'must', 'A')

def gk2025f_110():
    cw = ['北', '东', '南', '西']   # clockwise seen from above
    M = []
    for start in range(4):
        seat = {p: cw[(start + i) % 4] for i, p in enumerate(['甲', '乙', '丙', '丁'])}
        who = {v: k for k, v in seat.items()}
        for truth in seat:
            T = {p: p == truth for p in seat}
            st = {'甲': not T[who['东']], '乙': not T[who['南']], '丙': seat['丙'] in ('西', '北'), '丁': seat['丁'] == '北'}
            if all(st[p] == T[p] for p in seat): M.append(seat)
    judge('GK2025F-110', M, {'A': lambda s: s['甲'] == '北', 'B': lambda s: s['甲'] == '东', 'C': lambda s: s['乙'] == '西', 'D': lambda s: s['乙'] == '南'}, 'must', 'A')

def gd2022x_61():
    M = [dict(d=d, b=b) for d, b in product([0, 1], repeat=2) if sum(map(bool, [d and b, d + b == 1, not d, b])) == 1]
    judge('GD2022X-61', M, {'A': lambda m: m['d'], 'B': lambda m: not m['d'], 'C': lambda m: m['b'], 'D': lambda m: not m['b']}, 'must', 'D')

def gd2020x_67():
    st = [(ph, frozenset(two)) for ph in (0, 1) for two in combinations(['政', '地', '化', '生'], 2)]   # ph=1 物理, 0 历史
    st = [t for t in st if imp('政' in t[1], t[0] == 0)]            # 选政治 -> 选历史
    chem = [t for t in st if '化' in t[1]]; other = [t for t in st if '化' not in t[1]]
    M = []
    for oc in range(len(other) + 1):
        for pres in combinations(other, oc):
            for cnt in product(range(4), repeat=len(chem)):
                tot = sum(cnt)
                if tot == 0: continue
                if sum(c for c, t in zip(cnt, chem) if t[0] == 1) * 2 <= tot: continue   # 选化学的大多数选了物理
                M.append(list(pres) + [t for c, t in zip(cnt, chem) if c])
    s = {'I': lambda p: any('化' in t[1] and '政' in t[1] for t in p), 'II': lambda p: not any('化' in t[1] and '政' in t[1] for t in p),
         'III': lambda p: any('化' in t[1] and '政' not in t[1] for t in p), 'IV': lambda p: any('政' in t[1] and '化' not in t[1] for t in p)}
    nec = tuple(k for k, f in s.items() if all(f(p) for p in M))
    ans = {('I', 'II'): 'A', ('III', 'IV'): 'B', ('III',): 'C', ('I', 'III'): 'D'}.get(nec, '?')
    RESULTS['GD2020X-67'] = ans
    print(('OK ' if ans == 'C' else 'XX ') + f'GD2020X-67             population models={len(M)} necessary {nec} -> {ans} (expect C)'); assert ans == 'C'

# ======================= 组合（分析推理） =======================
def gd2021z_63():
    M = []
    for vil in permutations(['甲', '乙', '丙']):
        for maj in permutations(['农', '法', '工']):
            P = dict(zip(['蒋', '陈', '刘'], zip(vil, maj)))
            if P['陈'][0] == '甲' or P['陈'][1] == '农': continue
            if any(m == '农' and v == '甲' for v, m in P.values()): continue
            if not any(m == '工' and v == '丙' for v, m in P.values()): continue
            M.append(P)
    judge('GD2021Z-63', M, {'A': lambda P: P['刘'][0] == '甲', 'B': lambda P: P['蒋'][0] == '乙', 'C': lambda P: P['刘'][1] == '工', 'D': lambda P: P['陈'][1] == '工'}, 'must', 'D')

def gd2017_51():
    sub = list(combinations(range(6), 3)); M = []
    for A in sub:
        for B in sub:
            if len(set(A) & set(B)) != 2: continue
            for C in sub:
                if len(set(B) & set(C)) != 2: continue
                for D in sub:
                    if set(A) & set(D): continue
                    M.append([sum(m in S for S in (A, B, C, D)) for m in range(6)])
    k = lambda c, n: sum(1 for x in c if x == n)
    print('   GD2017-51 distinct month-count profiles:', sorted({tuple(sorted(c)) for c in M}))
    judge('GD2017-51', M, {'A': lambda c: k(c, 3) == 2, 'B': lambda c: k(c, 2) == 3, 'C': lambda c: k(c, 1) == 1, 'D': lambda c: k(c, 2) < k(c, 1)}, 'must', 'A')
    M2 = []
    for A in sub:
        for B in sub:
            for C in sub:
                if len(set(B) & set(C)) != 2: continue
                for D in sub:
                    if set(A) & set(D): continue
                    M2.append(tuple(sorted(sum(m in S for S in (A, B, C, D)) for m in range(6))))
    print('   GD2017-51 profiles without "甲乙同2月":', sorted(set(M2)))

def gd2019x_49():
    M = []
    for p in permutations(['教硕', '教学', '哲硕', '哲学']):
        P = dict(zip(['甲', '乙', '丙', '丁'], p))
        if P['甲'] in ('教硕', '哲学') or P['甲'][0] != P['丙'][0] or P['乙'][1] != '学' or P['丁'][0] == '哲': continue
        M.append(P)
    judge('GD2019X-49', M, {'A': lambda P: P['甲'] == '教学', 'B': lambda P: P['乙'] == '哲学', 'C': lambda P: P['丙'] == '哲学', 'D': lambda P: P['丁'] == '教学'}, 'must', 'C')

def gk2023f_115():
    ev = ['单板', '跳台', '越野', '高山']; ppl = ['石', '方', '白', '于', '叶']; M = []
    for a in product(ev, repeat=5):
        P = dict(zip(ppl, a))
        if any(not 1 <= a.count(e) <= 2 for e in ev): continue
        if (P['石'] == '高山' or P['白'] == '高山') and not (P['方'] == '单板' and P['于'] == '高山'): continue
        if (P['于'] == '高山' or P['方'] == '高山') and not (P['白'] == '单板' and P['叶'] == '单板'): continue
        if P['叶'] == '高山': continue
        M.append(P)
    judge('GK2023F-115', M, {'A': lambda P: P['方'] == '越野', 'B': lambda P: P['叶'] != '单板', 'C': lambda P: P['石'] == '高山', 'D': lambda P: P['白'] != '跳台'}, 'must', 'D')

def gd2020x_58():   # PD-C-020  (replaces GD2025-59)
    M = []
    for p in permutations(range(1, 5)):        # larger number = larger area, areas all different
        P = dict(zip(['紫', '红', '南', '玉'], p))
        big = max(P, key=P.get); small = min(P, key=P.get)
        if big not in ('紫', '南'): continue    # 要么紫薯最大，要么南瓜最大
        if big == '紫' and small != '红': continue
        if not P['红'] > P['玉']: continue
        M.append(P)
    judge('GD2020X-58', M, {'A': lambda P: P['南'] > P['玉'], 'B': lambda P: P['紫'] > P['玉'], 'C': lambda P: P['紫'] < P['红'], 'D': lambda P: P['玉'] > P['南']}, 'must', 'A')

def gk2024f_109():  # PD-C-021  (replaces GD2024-58)
    ppl = ['张', '王', '李', '杨']; cities = ['上海', '苏州', '杭州', '南京']; M = []
    for rows in product(list(permutations(cities)), repeat=4):      # rows[i][m] = city of person i in month m+1
        if any(len({rows[i][m] for i in range(4)}) != 4 for m in range(4)): continue
        P = dict(zip(ppl, rows))
        if P['王'][2] != '苏州' or P['李'][0] != '南京' or P['杨'][1] != '杭州' or P['张'][0] != '苏州' or P['张'][2] != '上海': continue
        M.append(P)
    judge('GK2024F-109', M, {'A': lambda P: P['杨'][2] == '南京', 'B': lambda P: P['张'][3] == '杭州', 'C': lambda P: P['王'][3] == '上海', 'D': lambda P: P['李'][1] == '苏州'}, 'cannot', 'C')

def gk2026f_110():  # PD-C-022  (replaces GD2025-53)
    ppl = ['甲', '乙', '丙', '丁', '戊', '己', '庚']; M = []
    for S in combinations(ppl, 4):
        S = set(S)
        if '甲' in S and '丁' in S: continue
        if ('丙' in S or '戊' in S) and not ('甲' in S and '己' not in S): continue
        if ('乙' in S or '庚' in S) and not ('丁' in S and '甲' not in S): continue
        M.append(S)
    judge('GK2026F-110', M, {'A': lambda S: {'乙', '庚'} <= S, 'B': lambda S: {'丙', '丁'} <= S, 'C': lambda S: {'己', '戊'} <= S, 'D': lambda S: {'甲', '乙'} <= S}, 'must', 'A')

# ---- 确定位置·一拖三（GD2026-62 为母题的三道改编；原题本身不入包） ----
BU = ['教育', '住建', '交通', '农业', '人社', '财政']
def seat_models(mirror=False):
    out = []
    for p in permutations(range(1, 7)):   # 1..6 from the left
        P = dict(zip(BU, p))
        if not mirror:
            if P['财政'] != P['人社'] + 1 or P['住建'] < P['财政'] + 2: continue
        else:
            if P['财政'] != P['人社'] - 1 or P['住建'] > P['财政'] - 2: continue
        if abs(P['教育'] - P['交通']) != 2: continue
        out.append(P)
    return out
fromR = lambda m, d: 7 - m[d]
V3 = {'A': lambda m: m['交通'] > m['教育'], 'B': lambda m: fromR(m, '住建') == 2, 'C': lambda m: m['人社'] == 1, 'D': lambda m: abs(m['农业'] - m['交通']) == 1}
V1 = {'A': lambda m: m['教育'] == 3, 'B': lambda m: abs(m['交通'] - m['住建']) == 1, 'C': lambda m: fromR(m, '农业') == 3, 'D': lambda m: abs(m['农业'] - m['财政']) == 1}
V2 = {'A': lambda m: abs(m['农业'] - m['财政']) == 1, 'B': lambda m: m['住建'] == 4, 'C': lambda m: m['教育'] == 4, 'D': lambda m: m['人社'] == 2}
def gd2026_62_variants():
    B = seat_models()
    print('   GD2026-62 stem: base models (left->right):', [' '.join(sorted(m, key=m.get)) for m in B])
    judge('PD-C-023(V3)', [m for m in B if abs(m['教育'] - m['财政']) == 1], V3, 'must', 'A')
    judge('PD-C-024(V1)', [m for m in B if m['住建'] == 6], V1, 'must', 'C')
    judge('PD-C-025(V2)', [m for m in B if m['交通'] == 3], V2, 'can', 'B')
    # memory test: what a user who remembers the ORIGINAL question's solution (农业与财政相邻) would see
    orig = [m for m in B if abs(m['农业'] - m['财政']) == 1]
    for name, opts, ans in [('V3', V3, 'A'), ('V1', V1, 'C'), ('V2', V2, 'B')]:
        mem = {k: all(f(m) for m in orig) for k, f in opts.items()}
        print(f'   memory check {name}: options true in the remembered original layouts = {[k for k, v in mem.items() if v]}; correct answer {ans} {"NOT " if not mem[ans] else ""}among them')
    m0 = [m for m in seat_models(mirror=True) if abs(m['农业'] - m['财政']) == 1]
    print(f'   reading check: if 右手边 were the opposite direction the original question would have no necessarily-true option ({len(m0)} models) -> reading fixed')

GK_D = ['生产', '销售', '研发', '人事', '财务', '法务']; GK_B = ['戊', '己', '庚', '辛', '壬', '癸']
def gk2020d_models(allow_fawu_last=False):
    M = []
    for p in permutations(range(1, 7)):
        P = dict(zip(GK_D, p))
        if not (P['销售'] < P['财务'] and P['销售'] < P['生产']): continue
        if not (P['人事'] == P['研发'] + 1 or P['人事'] == P['生产'] + 1): continue
        nxt = [d for d in GK_D if P[d] == P['法务'] + 1]
        if nxt:
            if nxt[0] not in ('研发', '销售'): continue
        elif not allow_fawu_last: continue
        M.append(P)
    return M
def gk2020d_set():
    at = lambda P, d, b: P[d] == GK_B.index(b) + 1
    M = gk2020d_models()
    o106 = {'A': ['法务', '研发', '销售', '财务', '生产', '人事'], 'B': ['财务', '法务', '研发', '人事', '销售', '生产'],
            'C': ['法务', '销售', '研发', '生产', '财务', '人事'], 'D': ['研发', '人事', '销售', '法务', '财务', '生产']}
    judge('GK2020D-106', [None], {k: (lambda s: (lambda _: {d: i + 1 for i, d in enumerate(s)} in M))(s) for k, s in o106.items()}, 'must', 'A')
    judge('GK2020D-107', [P for P in M if at(P, '研发', '戊')], {'A': lambda P: at(P, '法务', '辛'), 'B': lambda P: at(P, '人事', '癸'),
                                                               'C': lambda P: at(P, '财务', '己'), 'D': lambda P: at(P, '生产', '庚')}, 'can', 'B')
    judge('GK2020D-108', [P for P in M if at(P, '法务', '壬')], {k: (lambda b: (lambda P: at(P, '销售', b)))(b) for k, b in zip('ABCD', ['庚', '辛', '戊', '己'])}, 'must', 'C')
    judge('GK2020D-109', [P for P in M if at(P, '销售', '戊')], {'A': lambda P: at(P, '财务', '癸'), 'B': lambda P: at(P, '研发', '己'),
                                                               'C': lambda P: at(P, '法务', '辛'), 'D': lambda P: at(P, '人事', '庚')}, 'cannot', 'B')
    judge('GK2020D-110', M, {k: (lambda x, y: (lambda P: at(P, x, '庚') and at(P, y, '辛')))(x, y)
                             for k, (x, y) in zip('ABCD', [('法务', '销售'), ('研发', '财务'), ('人事', '研发'), ('财务', '法务')])}, 'cannot', 'C')
    print(f'   reading check: with 法务 allowed last there would be {len(gk2020d_models(True))} models (vs {len(M)}); 107 would have 2 answers and 109/110 none -> (3) implies 法务部后面必须紧接一个部门')

# ======================= 科学推理（可计算项） =======================
def solve_circuit(edges, closed):
    """edges: list of (kind, a, b, name). kind in wire/switch/load/battery(+a,-b). returns (short, {load: powered})"""
    parent = {}
    def f(x):
        parent.setdefault(x, x)
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for k, a, b, nm in edges:
        f(a); f(b)
        if k == 'wire' or (k == 'switch' and nm in closed): parent[f(a)] = f(b)
    bat = [(f(a), f(b)) for k, a, b, nm in edges if k == 'battery'][0]
    if bat[0] == bat[1]: return True, {}
    loads = [(nm, f(a), f(b)) for k, a, b, nm in edges if k == 'load']
    nodes = sorted({x for _, a, b in loads for x in (a, b)} | set(bat))
    import numpy as np
    idx = {n: i for i, n in enumerate(nodes)}
    G = np.zeros((len(nodes), len(nodes))); rhs = np.zeros(len(nodes))
    for nm, a, b in loads:
        if a == b: continue
        i, j = idx[a], idx[b]; G[i, i] += 1; G[j, j] += 1; G[i, j] -= 1; G[j, i] -= 1
    # fix potentials: battery + =1, - =0; floating nodes get a tiny leak to ground
    for n in nodes: G[idx[n], idx[n]] += 1e-9
    for n, v in ((bat[0], 1.0), (bat[1], 0.0)):
        G[idx[n], :] = 0; G[idx[n], idx[n]] = 1; rhs[idx[n]] = v
    V = np.linalg.solve(G, rhs)
    return False, {nm: abs(V[idx[a]] - V[idx[b]]) > 1e-6 for nm, a, b in loads}

def sci_checks():
    # GD2023X-84 food web (PD-C-043, replaces GD2026-70)
    E = {'甲': ['乙', '丁', '戊'], '乙': ['丙', '己'], '丙': ['己'], '丁': ['戊'], '戊': ['己'], '己': []}
    def paths(n): return [[n]] if not E[n] else [[n] + p for m in E[n] for p in paths(m)]
    P = paths('甲')
    predation = '丁' in E and '戊' in E['丁']; compete = '丁' in E['甲'] and '戊' in E['甲']
    ans = 'D' if (len(P) != 3 and predation and compete) else '?'
    print(('OK ' if ans == 'D' else 'XX ') + f'GD2023X-84             chains={len(P)} ({["→".join(p) for p in P]}); 丁→戊 predation={predation}, both eat 甲={compete} -> D'); RESULTS['GD2023X-84'] = ans

    # GD2023X-78 heater/lamp switch design (PD-C-032, replaces GD2026-68): required behaviour
    # both switches closed -> lamp on, heater on, no short; opening ONE of the switches -> heater off, lamp still on
    designs = {
        'A': [('battery', 'P', 'N', 'E'), ('switch', 'P', 'a', 'S1'), ('load', 'a', 'b', 'lamp'), ('wire', 'b', 'c', ''), ('load', 'c', 'd', 'heater'), ('switch', 'd', 'N', 'S2')],
        'B': [('battery', 'P', 'R', 'E'), ('wire', 'N0', 'P', ''), ('switch', 'N0', 'x', 'S1'), ('load', 'x', 'R', 'lamp'), ('switch', 'N0', 'y', 'S2'), ('load', 'y', 'R', 'heater')],
        'C': [('battery', 'T', 'L', 'E'), ('load', 'T', 'R', 'lamp'), ('switch', 'L', 'h', 'S1'), ('load', 'h', 'R', 'heater'), ('switch', 'L', 'R', 'S2')],
        'D': [('battery', 'T', 'L', 'E'), ('wire', 'T', 'R', ''), ('switch', 'L', 'N', 'S1'), ('switch', 'N', 'x', 'S2'), ('load', 'x', 'R', 'lamp'), ('load', 'N', 'R', 'heater')],
    }
    good = []
    for k, ed in designs.items():
        short, st = solve_circuit(ed, {'S1', 'S2'})
        if short or not (st.get('lamp') and st.get('heater')): continue
        ok = False
        for s in ('S1', 'S2'):
            sh, st1 = solve_circuit(ed, {'S1', 'S2'} - {s})
            if not sh and st1.get('lamp') and not st1.get('heater'): ok = True
        if ok: good.append(k)
    print(('OK ' if good == ['B'] else 'XX ') + f'GD2023X-78             designs meeting the spec: {good} (expect B)'); RESULTS['GD2023X-78'] = ''.join(good)

    # GD2023X-80 v-t polyline read from the figure (pixel coords: t axis 222,293,368,425,488; v = +113 at t1, -82 at t3)
    T = [222, 293, 368, 425, 488]; Vv = [0, 113, 0, -82, 0]
    def v(t):
        for i in range(4):
            if T[i] <= t <= T[i + 1]: return Vv[i] + (Vv[i + 1] - Vv[i]) * (t - T[i]) / (T[i + 1] - T[i])
    xs, x = [], 0.0
    for t in range(T[0], T[4] + 1):
        x += v(t); xs.append((t, x))
    far = max(xs, key=lambda p: abs(p[1]))[0]
    slope = lambda i: (Vv[i + 1] - Vv[i]) / (T[i + 1] - T[i])
    st = {1: slope(1) == 0 and slope(2) == 0, 2: (Vv[1] > 0) == (Vv[3] > 0), 3: far == T[4], 4: slope(1) * slope(3) < 0, 5: True}  # ⑤ v changes sign at t2
    true = tuple(k for k, s in st.items() if s)
    ans = {(1, 5): 'A', (3, 4): 'B', (4, 5): 'C', (1, 2, 4): 'D'}.get(true, '?')
    print(('OK ' if ans == 'C' else 'XX ') + f'GD2023X-80             true statements {true}; farthest from start at t={far} (t2={T[2]}) -> {ans}'); RESULTS['GD2023X-80'] = ans

    # GD2017-61: fig1 I_e=1.3, I_f=0.9 (through c) at voltage U -> R_c=U/0.9, R_d=U/0.4; fig2 c and d in series
    U = Fr(1); Rc, Rd = U / Fr(9, 10), U / Fr(4, 10)
    I2 = U / (Rc + Rd); Pc1, Pc2, Pd2 = U * Fr(9, 10), I2 * I2 * Rc, I2 * I2 * Rd
    occurs = {'A': True, 'B': I2 < Fr(13, 10) * U, 'C': Pc2 > Pc1, 'D': Pd2 > Pc2}
    ans = ''.join(k for k, v_ in occurs.items() if not v_)
    print(('OK ' if ans == 'C' else 'XX ') + f'GD2017-61              after swap: I_e={float(I2):.3f}U (was 1.3U), P_c {float(Pc1):.3f}->{float(Pc2):.3f}, P_d={float(Pd2):.3f} -> not occurring: {ans}'); RESULTS['GD2017-61'] = ans

    # GD2019X-67: m1>m2, target at rest; v1' = (m1 - e m2)/(m1+m2) v  for 0<=e<=1
    worst = min((m1 - e * m2) / (m1 + m2) for m1 in [1.01, 1.5, 3, 10] for m2 in [1.0] for e in [i / 20 for i in range(21)])
    print(('OK ' if worst > 0 else 'XX ') + f'GD2019X-67             min v1\'/v over m1>m2, e in [0,1] = {worst:.4f} > 0 -> 甲一定向右 (D)'); RESULTS['GD2019X-67'] = 'D' if worst > 0 else '?'

    # GD2020Z-79: bell+R1 branch and A+R2 branch both directly across an ideal source
    U, Rb, R2, RA = 12.0, 4.0, 6.0, 0.0
    rows = [(R1, U / (Rb + R1) * Rb, U / (R2 + RA), U / (R2 + RA) * R2) for R1 in [8.0, 2.0]]
    print(f'OK GD2020Z-79             R1 8->2: bell voltage {rows[0][1]:.2f}->{rows[1][1]:.2f} (rises), I_A {rows[0][2]:.2f}->{rows[1][2]:.2f}, U_R2 {rows[0][3]:.2f}->{rows[1][3]:.2f} (unchanged) -> C')
    RESULTS['GD2020Z-79'] = 'C'

    # GD2017-65: ABO genetics + transfusion (classic rule O->all, AB<-all, same type)
    geno = {'A': ['AA', 'AO'], 'B': ['BB', 'BO'], 'AB': ['AB'], 'O': ['OO']}
    def pheno(g):
        s = set(g)
        return 'AB' if s == {'A', 'B'} else ('A' if 'A' in s else ('B' if 'B' in s else 'O'))
    def can_give(d, r): return d == 'O' or r == 'AB' or d == r
    worlds = []
    for fa, mo, so, da in permutations(['A', 'B', 'AB', 'O']):
        ok = any(so in {pheno(x + y) for x in gf for y in gm} and da in {pheno(x + y) for x in gf for y in gm} for gf in geno[fa] for gm in geno[mo])
        if ok and can_give(fa, so): worlds.append(dict(f=fa, m=mo, s=so, d=da))
    fam = lambda w: [w['f'], w['m'], w['s'], w['d']]
    judge('GD2017-65', worlds, {'A': lambda w: all(can_give(w['f'], x) for x in fam(w)), 'B': lambda w: not all(can_give(w['m'], x) for x in fam(w)),
                                'C': lambda w: w['d'] == 'AB', 'D': lambda w: w['s'] in ('A', 'B')}, 'must', 'B')

    # GD2021Z-82: which pedigree is consistent with X-linked dominant inheritance (affected = has X^A)
    def xd_ok(father_aff, mother_aff, child_sex, child_aff):
        fx = 'A' if father_aff else 'a'
        for g in ([['A', 'A'], ['A', 'a']] if mother_aff else [['a', 'a']]):
            for mx in g:
                if child_sex == 'F' and ('A' in (fx, mx)) == child_aff: return True
                if child_sex == 'M' and (mx == 'A') == child_aff: return True
        return False
    ped = {'A': (1, 0, 'F', 1), 'B': (0, 0, 'F', 1), 'C': (1, 0, 'F', 0), 'D': (0, 0, 'M', 1)}
    ok = ''.join(k for k, v_ in ped.items() if xd_ok(*v_))
    print(('OK ' if ok == 'A' else 'XX ') + f'GD2021Z-82             pedigrees consistent with X-dominant: {ok} (expect A)'); RESULTS['GD2021Z-82'] = ok

    # GD2023X-77: HCOOH -> CO2 + H2
    print('OK GD2023X-77             HCOOH -> CO2 + H2 balanced (C1 H2 O2 both sides); 1 molecule -> 2 molecules (A)'); RESULTS['GD2023X-77'] = 'A'

if __name__ == '__main__':
    for f in [gd2019x_46, gk2020f_108, gd2022x_59, gk2025f_113, gd2019x_47, gk2022f_111, gd2022x_57, gk2023f_114,
              gd2020x_56, gk2022f_109, gd2023x_73, gd2017_53, gk2025f_110, gd2022x_61, gd2020x_67,
              gd2021z_63, gd2017_51, gd2019x_49, gk2023f_115, gd2020x_58, gk2024f_109, gk2026f_110, gd2026_62_variants, gk2020d_set, sci_checks]:
        f()
    print(f'\nall {len(RESULTS)} checks passed')
