from itertools import permutations, product, combinations
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pdc')
from verify_logic import report, imp, gd2026_62, R

def show_base_2026_62():
    base = gd2026_62()
    print('GD2026-62 base models:')
    for m in base: print('   ', ' '.join(sorted(m, key=m.get)))

# GK2020D 106-110: 6 depts, buildings 戊己庚辛壬癸 front->back (positions 1..6)
def gk2020d():
    D = ['生产', '销售', '研发', '人事', '财务', '法务']
    M = []
    for p in permutations(range(1, 7)):
        P = dict(zip(D, p))
        if not (P['销售'] < P['财务'] and P['销售'] < P['生产']): continue
        if not (P['人事'] == P['研发'] + 1 or P['人事'] == P['生产'] + 1): continue
        nxt = [d for d in D if P[d] == P['法务'] + 1]
        if not nxt or nxt[0] not in ('研发', '销售'): continue
        M.append(P)
    B = ['戊', '己', '庚', '辛', '壬', '癸']
    def at(P, d, b): return P[d] == B.index(b) + 1
    print('GK2020D models:', len(M))
    for m in M: print('   ', ' '.join(sorted(m, key=m.get)))
    # 106: which order (front->back) satisfies
    o106 = {'A': ['法务', '研发', '销售', '财务', '生产', '人事'], 'B': ['财务', '法务', '研发', '人事', '销售', '生产'],
            'C': ['法务', '销售', '研发', '生产', '财务', '人事'], 'D': ['研发', '人事', '销售', '法务', '财务', '生产']}
    ok = [k for k, seq in o106.items() if {d: i + 1 for i, d in enumerate(seq)} in M]
    print('106 ->', ok); R['GK2020D-106'] = ok
    M7 = [P for P in M if at(P, '研发', '戊')]
    report('GK2020D-107', M7, {'A': lambda P: at(P, '法务', '辛'), 'B': lambda P: at(P, '人事', '癸'), 'C': lambda P: at(P, '财务', '己'), 'D': lambda P: at(P, '生产', '庚')}, 'can')
    M8 = [P for P in M if at(P, '法务', '壬')]
    report('GK2020D-108', M8, {'A': lambda P: at(P, '销售', '庚'), 'B': lambda P: at(P, '销售', '辛'), 'C': lambda P: at(P, '销售', '戊'), 'D': lambda P: at(P, '销售', '己')}, 'must')
    M9 = [P for P in M if at(P, '销售', '戊')]
    report('GK2020D-109', M9, {'A': lambda P: at(P, '财务', '癸'), 'B': lambda P: at(P, '研发', '己'), 'C': lambda P: at(P, '法务', '辛'), 'D': lambda P: at(P, '人事', '庚')}, 'cannot')
    report('GK2020D-110', M, {'A': lambda P: at(P, '法务', '庚') and at(P, '销售', '辛'), 'B': lambda P: at(P, '研发', '庚') and at(P, '财务', '辛'),
                              'C': lambda P: at(P, '人事', '庚') and at(P, '研发', '辛'), 'D': lambda P: at(P, '财务', '庚') and at(P, '法务', '辛')}, 'cannot')

def gk2021f_114():
    ppl = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛']
    M = []
    for p in permutations(range(1, 9)):
        P = dict(zip(ppl, p))
        if abs(P['甲'] - P['丙']) != 4: continue
        if abs(P['乙'] - P['己']) != 3: continue
        if P['庚'] - P['丁'] != 3: continue
        if abs(P['辛'] - P['戊']) != 2: continue
        M.append(P)
    print('GK2021F-114 models', len(M), 'positions of 丁 seen:', sorted({P['丁'] for P in M}))
    report('GK2021F-114', M, {'A': lambda P: P['丁'] == 1, 'B': lambda P: P['丁'] == 2, 'C': lambda P: P['丁'] == 3, 'D': lambda P: P['丁'] == 4}, 'cannot')

def gk2017f_115():
    jobs = ['行政', '销售', '研发', '安保']; ppl = ['张', '王', '李', '赵']
    M = []
    for p in permutations(jobs):
        P = dict(zip(ppl, p))
        if P['张'] in ('行政', '安保'): continue
        if P['王'] in ('行政', '研发'): continue
        if not imp(P['张'] != '研发', P['赵'] != '行政'): continue
        if P['李'] in ('行政', '安保'): continue
        if P['赵'] in ('研发', '安保'): continue
        M.append(P)
    report('GK2017F-115', M, {'A': lambda P: P['张'] == '销售' and P['李'] == '研发', 'B': lambda P: P['赵'] == '研发' and P['李'] == '销售',
                              'C': lambda P: P['李'] == '销售' and P['张'] == '研发', 'D': lambda P: P['李'] == '研发' and P['赵'] == '安保'}, 'must')

def gk2026f_110():
    ppl = ['甲', '乙', '丙', '丁', '戊', '己', '庚']
    M = []
    for S in combinations(ppl, 4):
        S = set(S)
        if '甲' in S and '丁' in S: continue
        if ('丙' in S or '戊' in S) and not ('甲' in S and '己' not in S): continue
        if ('乙' in S or '庚' in S) and not ('丁' in S and '甲' not in S): continue
        M.append(S)
    print('GK2026F-110 models', M)
    report('GK2026F-110', M, {'A': lambda S: {'乙', '庚'} <= S, 'B': lambda S: {'丙', '丁'} <= S, 'C': lambda S: {'己', '戊'} <= S, 'D': lambda S: {'甲', '乙'} <= S}, 'must')

def gk2025f_115():
    ppl = ['甲', '乙', '丙', '丁', '戊', '己', '庚']
    M = []
    for w in product([0, 1], repeat=7):
        W = dict(zip(ppl, w))
        if W['戊'] + W['己'] + W['庚'] < 2: continue
        if (W['甲'] or W['丙'] or W['戊']) and not ((not W['丁']) and (not W['己'])): continue
        if (W['乙'] or W['戊'] or W['己']) and not (W['丁'] and not W['丙']): continue
        M.append(W)
    print('GK2025F-115 models', M)
    report('GK2025F-115', M, {k: (lambda p: (lambda W: W[p]))(p) for k, p in zip('ABCD', ['甲', '乙', '丙', '丁'])}, 'must')

def gk2024f_115():
    ppl = ['甲', '乙', '丙', '丁']
    M = []
    for w in product([0, 1], repeat=4):
        a, b, c, d = w
        if not imp((not a) and (not b), c): continue
        if not imp(b or c, d): continue
        if not imp(a or b, c and not d): continue
        M.append(w)
    print('GK2024F-115 models', M)
    report('GK2024F-115', M, {'A': lambda w: w[2] and w[3], 'B': lambda w: w[0] and w[3], 'C': lambda w: w[0] and w[1], 'D': lambda w: w[1] and w[2]}, 'must')

def gk2018f_109():
    # standing: some people reach standard. 张: nobody; 孙: somebody; 王: (champ or national) reach. exactly one correct.
    M = []
    for anyone, champ, nat, alll in product([0, 1], repeat=4):
        if (champ or nat) and not anyone: continue
        if alll and not (anyone and champ and nat): continue
        s = [not anyone, anyone, champ or nat]
        if sum(map(bool, s)) == 1: M.append(dict(anyone=anyone, champ=champ, nat=nat, alll=alll))
    report('GK2018F-109', M, {'A': lambda m: not m['anyone'], 'B': lambda m: m['alll'], 'C': lambda m: m['champ'], 'D': lambda m: not m['nat']}, 'must')

def gd2025_64():
    sites = ['欢乐', '动物', '艺术', '人民', '博物']
    M = []
    for v in product([0, 1], repeat=5):
        S = dict(zip(sites, v))
        if not (S['欢乐'] or S['动物']): continue
        if not (S['艺术'] or S['欢乐'] or S['人民']): continue
        if S['动物'] + S['人民'] + S['博物'] < 2: continue
        if S['动物'] and S['艺术']: continue
        M.append(S)
    report('GD2025-64', M, {'A': lambda S: S['博物'], 'B': lambda S: S['动物'] or S['艺术'], 'C': lambda S: S['人民'] or S['欢乐'], 'D': lambda S: sum(S.values()) >= 3}, 'must')

def gd2026_63():
    vil = ['甲', '乙', '丙', '丁']; aw = ['文旅', '非遗', '生态', '数字']
    out = {}
    for tie_mode in ('only_stated_tie', 'ties_allowed'):
        M = []
        for a in permutations(aw):
            A = dict(zip(vil, a)); V = {v: k for k, v in A.items()}
            for inc in product(range(1, 5), repeat=4):
                I = dict(zip(vil, inc))
                if tie_mode == 'only_stated_tie':
                    # only 甲 and 数字村 tie; all other pairs distinct
                    pairs = [(x, y) for x, y in combinations(vil, 2)]
                    bad = False
                    for x, y in pairs:
                        if I[x] == I[y] and {x, y} != {'甲', V['数字']}: bad = True
                    if bad: continue
                if not I[V['文旅']] > I['丙']: continue
                if V['数字'] == '甲' or I['甲'] != I[V['数字']]: continue
                mx = max(I.values())
                if I['甲'] == mx: continue
                if not I[V['生态']] > I['丁']: continue
                if not I['丙'] > I[V['非遗']]: continue
                M.append((A, I))
        # canonicalise income to ranks
        opts = {'A': lambda m: sorted(set(m[1].values()), reverse=True).index(m[1]['甲']) == 1 and list(m[1].values()).count(max(m[1].values())) >= 1,
                'B': lambda m: m[0]['乙'] == '文旅', 'C': lambda m: m[0]['丙'] == '数字', 'D': lambda m: m[0]['丁'] == '非遗'}
        res = {k: (all(f(m) for m in M), any(f(m) for m in M)) for k, f in opts.items()}
        out[tie_mode] = (len(M), {k: ('ALL' if x else ('SOME' if y else 'NONE')) for k, (x, y) in res.items()},
                         sorted({tuple(m[0][v] for v in vil) for m in M}))
    for k, v in out.items(): print('GD2026-63', k, v)

def gd2018_54_note():
    print('GD2018-54: I false (non-tea drinker), III false (有的 does not imply 有的不); II relies on reading 或者红或者绿 as exhaustive of tea kinds -> A')

def gd2017_56():
    M = []
    for who, kai, jing in product(['张', '李'], [0, 1], [0, 1]):
        if who == '张' and not kai: continue
        if who == '李' and not jing: continue
        M.append(dict(who=who, kai=kai, jing=jing))
    report('GD2017-56', M, {'A': lambda m: m['kai'] and m['jing'], 'B': lambda m: imp(m['kai'], m['who'] == '张'), 'C': lambda m: imp(m['jing'], m['who'] == '李'),
                            'D': lambda m: imp(not m['kai'], m['jing'])}, 'must')

def gd2020x_58():
    crops = ['紫', '红', '南', '玉']
    M = []
    for p in permutations(range(1, 5)):
        P = dict(zip(crops, p))  # larger = bigger area
        big = max(P, key=P.get); small = min(P, key=P.get)
        if big not in ('紫', '南'): continue
        if big == '紫' and small != '红': continue
        if not P['红'] > P['玉']: continue
        M.append(P)
    report('GD2020X-58', M, {'A': lambda P: P['南'] > P['玉'], 'B': lambda P: P['紫'] > P['玉'], 'C': lambda P: P['紫'] < P['红'], 'D': lambda P: P['玉'] > P['南']}, 'must')

def gk2017f_114():
    # 3 people with tax amounts; help relation H: 李->王, 王->赵. Tax 李 > 赵. Options
    M = []
    for tl, tw, tz in product(range(3), repeat=3):
        if not tl > tz: continue
        M.append(dict(l=tl, w=tw, z=tz))
    report('GK2017F-114', M, {'A': lambda m: m['w'] > m['z'], 'B': lambda m: m['l'] == m['w'],
                              'C': lambda m: (m['w'] > m['l']) or (m['z'] > m['w']), 'D': lambda m: (m['w'] < m['l']) or (m['z'] < m['w'])}, 'must')

if __name__ == '__main__':
    show_base_2026_62(); gk2020d(); gk2021f_114(); gk2017f_115(); gk2026f_110(); gk2025f_115(); gk2024f_115(); gk2018f_109()
    gd2025_64(); gd2026_63(); gd2018_54_note(); gd2017_56(); gd2020x_58(); gk2017f_114()
