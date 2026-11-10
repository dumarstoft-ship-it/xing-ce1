"""PD4C / D12 verification script (第4轮判断日：条件与必然性 + 组合 + 科学推理).
Every logic item is solved by exhaustive enumeration of all models consistent with the stem (independent of the source analysis);
where a wording could be read in more than one way, every reading is enumerated and the results are printed side by side.
Every computable science item is re-computed.
Run:  python3 -I verify_d12.py
Each check prints the option(s) satisfying the ask and asserts it equals the expected (checked) answer;
crosscheck() then compares every result with checked_answer / source_answer in ../questions.jsonl."""
import sys, math, random
from itertools import permutations, product, combinations
from fractions import Fraction as Fr

RESULTS = {}
def imp(a, b): return (not a) or b

def stat_of(models, opts):
    st = {}
    for k, f in opts.items():
        v = [bool(f(m)) for m in models]
        st[k] = 'ALL' if all(v) else ('SOME' if any(v) else 'NONE')
    return st

SEL = {'must': lambda s: s == 'ALL', 'can': lambda s: s != 'NONE', 'cannot': lambda s: s == 'NONE', 'notmust': lambda s: s != 'ALL'}
def judge(qid, models, opts, mode, expect, note='', record=True):
    """mode: must = true in every model; can = true in some model; cannot = true in no model; notmust = not true in every model"""
    assert models, qid + ': no model satisfies the stem'
    stat = stat_of(models, opts)
    ans = ''.join(k for k, s in stat.items() if SEL[mode](s))
    if record: RESULTS[qid] = ans
    print(f"{'OK ' if ans == expect else 'XX '}{qid:32s} models={len(models):7d} ask={mode:7s} -> {ans:4s} (expect {expect})  {stat} {note}")
    assert ans == expect, qid
    return ans

def record(qid, ans, expect, msg):
    RESULTS[qid] = ans
    print(('OK ' if ans == expect else 'XX ') + f'{qid:32s} {msg} -> {ans} (expect {expect})')
    assert ans == expect, qid

def reading(qid, label, models, opts, mode):
    """print a non-recorded alternative reading"""
    if not models:
        print(f'   reading [{label}] {qid}: 无模型（该读法与题干自身矛盾）'); return None
    stat = stat_of(models, opts)
    ans = ''.join(k for k, s in stat.items() if SEL[mode](s))
    print(f'   reading [{label}] {qid}: models={len(models)} -> {ans or "(无选项成立)"} {stat}')
    return ans

B = (0, 1)
# =====================================================================================
# D12-C1 条件与必然性
# =====================================================================================
def gk2017f_113():
    # 三个数（允许相等也一并穷举）；教练的话为假 <=> 至少两人说假话。问“可能”的顺序。
    M = []
    for A, Bn, C in product(range(1, 4), repeat=3):
        lies = (not Bn > C) + (not A < C) + (not A < Bn)
        if lies >= 2: M.append((A, Bn, C))
    judge('GK2017F-113', M, {'A': lambda m: m[0] > m[1] > m[2], 'B': lambda m: m[2] > m[1] > m[0],
                             'C': lambda m: m[1] > m[2] > m[0], 'D': lambda m: m[1] > m[0] > m[2]}, 'can', 'A')

def hb2022_110():
    M = []
    for a, b in product(B, repeat=2):
        s = [imp(a, b), bool(a), bool(a and not b), imp(not a, b)]
        if sum(s) == 2: M.append((a, b))
    judge('HB2022-110', M, {'A': lambda m: m == (1, 1), 'B': lambda m: m == (0, 0), 'C': lambda m: m == (1, 0), 'D': lambda m: m == (0, 1)}, 'must', 'D', note=str(M))

def sd2023_68():
    # 个体类型 (法学 L, 法律职业资格 Z, 教师资格 T, 公务员 G, 逻辑学 X)。全称：L→Z，Z→T，X→¬T。
    # “一定为假”= 选项描述的那种人在任何满足题干的情形中都不可能存在。存在句（有些法学生是公务员、有些逻辑学生是公务员）只保证相应类型非空。
    types = [t for t in product(B, repeat=5) if imp(t[0], t[1]) and imp(t[1], t[2]) and imp(t[4], not t[2])]
    assert any(t[0] and t[3] for t in types) and any(t[4] and t[3] for t in types)
    desc = {'A': lambda t: t[2] and not t[4], 'B': lambda t: t[3] and not t[1] and not t[4], 'C': lambda t: t[1] and not t[0], 'D': lambda t: t[4] and t[1]}
    ans = ''.join(k for k, f in desc.items() if not any(f(t) for t in types))
    record('SD2023-68', ans, 'D', f"可存在的个体类型 {len(types)} 种；各选项描述的人能否存在：{ {k: any(f(t) for t in types) for k, f in desc.items()} }")

def gk2016f_111():
    names = 'ABCDEF'; M = []
    for v in product(B, repeat=6):
        x = dict(zip(names, v))
        if (x['A'] or x['B']) and imp((not x['C']) or (not x['D']), not x['A']) and imp(not x['C'], not x['F']) and imp(x['B'], x['E']) and not x['E']:
            M.append(x)
    st = {n: ('ALL' if all(m[n] for m in M) else 'NONE' if not any(m[n] for m in M) else 'SOME') for n in names}
    truth = {'A': st['F'] == 'SOME', 'B': st['A'] == 'NONE', 'C': st['C'] == 'SOME' or st['D'] == 'SOME', 'D': st['B'] == 'ALL'}
    record('GK2016F-111', ''.join(k for k, v in truth.items() if v), 'A', f'models={len(M)}，各节目通过与否：{st}')

def gdxd2020sw_24():
    M = []
    for g in product(B, repeat=3):
        n = sum(g); s = [not g[0], n == 1, n == 3, n == 0]
        if sum(s) == 1: M.append(g)
    poss = sorted({sum(g) for g in M})
    judge('GDXD2020SW-24', M, {k: (lambda n: (lambda g: sum(g) == n))(n) for k, n in zip('ABCD', range(4))}, 'cannot', 'A', note=f'可能的实现个数={poss}')
    # 读法对照：乙“只能实现其中一个”读成“至多实现一个”
    M2 = [g for g in product(B, repeat=3) if sum([not g[0], sum(g) <= 1, sum(g) == 3, sum(g) == 0]) == 1]
    reading('GDXD2020SW-24', '乙=至多实现一个', M2, {k: (lambda n: (lambda g: sum(g) == n))(n) for k, n in zip('ABCD', range(4))}, 'cannot')

def js2021a_97():
    # 只需考察李女士本人：诗词 s、书法 f、合唱 h、戏迷 x。题干：s∨f；s→¬h；h。结论：x。
    base = [m for m in product(B, repeat=4) if (m[0] or m[1]) and imp(m[0], not m[2]) and m[2]]
    prem = {'A': lambda s, f, h, x: not s, 'B': lambda s, f, h, x: imp(x, f), 'C': lambda s, f, h, x: not f, 'D': lambda s, f, h, x: imp(not x, not f)}
    res = {}
    for k, p in prem.items():
        W = [m for m in base if p(*m)]
        res[k] = ('矛盾(无模型)' if not W else ('推出' if all(m[3] for m in W) else '推不出'))
    record('JS2021A-97', ''.join(k for k, v in res.items() if v == '推出'), 'D', f'题干下李女士的可能情形 {base}；各选项补入后：{res}')

def sd2021_71():
    ppl = 'FGHJ'; M = []
    for jobs in permutations(['研', '作曲', '老师', '公务员']):
        J = dict(zip(ppl, jobs))
        for wife in B:
            s = {'F': J['G'] != '作曲', 'G': J['H'] == '研', 'H': J['J'] != '公务员', 'J': bool(wife)}
            right = [p for p in ppl if s[p]]
            if len(right) == 1 and J[right[0]] == '研': M.append(dict(J=J, wife=wife))
    judge('SD2021-71', M, {'A': lambda m: not m['wife'], 'B': lambda m: m['J']['F'] == '研', 'C': lambda m: m['J']['G'] == '老师', 'D': lambda m: m['J']['H'] == '公务员'},
          'cannot', 'D', note=str([(m['J'], m['wife']) for m in M]))

def js2023a_103():
    hs = [165, 168, 170, 172]; ppl = '甲乙丙丁'; out = {}
    for rd in ('合取为假', '分句全假'):
        M = []
        for hp in permutations(hs):
            H = dict(zip(ppl, hp))
            for thin in combinations(ppl, 2):
                T = {p: p in thin for p in ppl}
                st = {'甲': [H['甲'] < 170], '乙': [H['丙'] == 172, T['丙']], '丙': [H['丁'] == 168, not T['丁']], '丁': [H['乙'] == 165, T['乙']]}
                ok = True
                for p in ppl:
                    if T[p]: ok = ok and all(st[p])
                    else: ok = ok and ((not all(st[p])) if rd == '合取为假' else (not any(st[p])))
                if ok: M.append((H, T))
        out[rd] = M
    opts = {'A': lambda m: m[0]['甲'] == 165 and not m[1]['甲'], 'B': lambda m: m[0]['乙'] == 170 and m[1]['乙'],
            'C': lambda m: m[0]['丙'] == 172 and m[1]['丙'], 'D': lambda m: m[0]['丁'] == 168 and not m[1]['丁']}
    judge('JS2023A-103(合取为假)', out['合取为假'], opts, 'must', 'D', note=str([(m[0], ''.join(p for p in ppl if m[1][p])) for m in out['合取为假']]))
    reading('JS2023A-103', '说假话=每个分句都假', out['分句全假'], opts, 'must')

def sz2020sw_80():
    # 世界 = (真凶, 三人各自指控对象)。说真话 <=> 所指控的人是真凶。
    ppl = '甲乙丙'; W = []
    for k in ppl:
        for acc in product(*[[q for q in ppl if q != p] for p in ppl]):
            A = dict(zip(ppl, acc)); W.append(dict(k=k, A=A, t={p: A[p] == k for p in ppl}))
    # 老赵当时知道：甲说真话；丙说的真/假（值为 tv）；不知道乙的真假，也不知道谁指控谁。
    info = {tv: [w for w in W if w['t']['甲'] and w['t']['丙'] == tv] for tv in (True, False)}
    ks = {tv: sorted({w['k'] for w in info[tv]}) for tv in info}
    could = [tv for tv in info if len(ks[tv]) == 1]           # 当时能唯一推出真凶的情形
    M = [w for tv in could for w in info[tv]]
    judge('SZ2020SW-80', M, {'A': lambda w: w['k'] == '乙', 'B': lambda w: w['t']['乙'], 'C': lambda w: not w['t']['丙'], 'D': lambda w: w['k'] == '丙'}, 'must', 'A',
          note=f'丙真话→真凶只能是{ks[True]}；丙假话→真凶可能是{ks[False]}（当时推不出）；故被告知的是“丙说真话”')


# =====================================================================================
# D12-C2 组合（单题）：匹配、分组、排序与座位
# =====================================================================================
def sz20201_33():
    # 5 人 × 5 轮，每轮 5 人各拿不同颜色的球（同一轮各不相同），每人 5 轮拿遍 5 色 —— 5 阶拉丁方。
    col = '黑白蓝红黄'; A = tuple(col); P = list(permutations(col)); M = []
    for Bz in P:
        if A[4] != Bz[1] or any(A[i] == Bz[i] for i in range(5)): continue
        for C in P:
            if C[1] != A[0] or C[4] != Bz[3] or any(C[i] in (A[i], Bz[i]) for i in range(5)): continue
            for D in P:
                if D[2] != C[0] or D[4] != C[2] or any(D[i] in (A[i], Bz[i], C[i]) for i in range(5)): continue
                for E in P:
                    if Bz[3] != E[2] or any(E[i] in (A[i], Bz[i], C[i], D[i]) for i in range(5)): continue
                    M.append(dict(乙=''.join(Bz), 丙=''.join(C), 丁=''.join(D), 戊=''.join(E)))
    judge('SZ20201-33', M, {'A': lambda m: m['乙'] == '白黄红黑蓝', 'B': lambda m: m['丙'] == '红黑黄白蓝', 'C': lambda m: m['丁'] == '白蓝黄黑红', 'D': lambda m: m['戊'] == '蓝黑白黄红'},
          'must', 'C', note=str(M))

def sz20201_38():
    # 每人 4 次击中 4 只不同的地鼠（1—7 号），得分和 17。读法 S：“得分相同”指分值相同（不要求在同一次）；读法 R：指同一次（第 i 次对第 i 次）得分相同。
    S = [frozenset(c) for c in combinations(range(1, 8), 4) if sum(c) == 17]
    M = []
    for D, C, Q in product(S, repeat=3):          # D=盯得准 C=出得快 Q=敲得狠
        a, b = Q & D, Q & C
        if len(D & C) == 1 and any(set(x) <= D and (Q - set(x)) <= C for x in combinations(sorted(Q), 2)):
            M.append(dict(D=D, C=C, Q=Q))
    judge('SZ20201-38', M, {k: (lambda n: (lambda m: n in m['D'] and n in m['C']))(n) for k, n in zip('ABCD', (2, 3, 4, 6))}, 'must', 'D',
          note=f"和为17的四元组只有 {[sorted(s) for s in S]}；解：{[(sorted(m['D']), sorted(m['C']), sorted(m['Q'])) for m in M]}")
    seqs = [p for s in S for p in permutations(sorted(s))]; R = []
    for D in seqs:
        for C in seqs:
            if sum(D[i] == C[i] for i in range(4)) != 1: continue
            for Q in seqs:
                qd = {i for i in range(4) if Q[i] == D[i]}; qc = {i for i in range(4) if Q[i] == C[i]}
                if len(qd) == 2 and len(qc) == 2 and not qd & qc: R.append(dict(D=set(D), C=set(C), Q=set(Q)))
    reading('SZ20201-38', '同一次得分相同', R, {k: (lambda n: (lambda m: n in m['D'] and n in m['C']))(n) for k, n in zip('ABCD', (2, 3, 4, 6))}, 'must')

def zj2025a_104():
    # 石头 0 指、剪刀 2 指、布 5 指；先累计赢两次者获胜，比赛随即结束。穷举不超过 8 轮的全部对局（多出的轮次只能是双方都出石头的平局）。
    beats = {(0, 2), (2, 5), (5, 0)}          # (a, b)：a 赢 b
    G = []
    def rec(seq, wl, ww, fl, fw):
        if wl == 2 or ww == 2:
            if fl == 9 and fw == 5: G.append(tuple(seq))
            return
        if len(seq) == 8 or fl > 9 or fw > 5: return
        for a in (0, 2, 5):
            for b in (0, 2, 5):
                rec(seq + [(a, b)], wl + ((a, b) in beats), ww + ((b, a) in beats), fl + a, fw + b)
    rec([], 0, 0, 0, 0)
    def res(g): return ['L' if (a, b) in beats else 'W' if (b, a) in beats else '-' for a, b in g]
    def winner(g): r = res(g); return 'L' if r.count('L') == 2 else 'W'
    def consec_win(g, who):
        r = res(g); return winner(g) == who and any(r[i] == r[i + 1] == who for i in range(len(r) - 1))
    def three_draws(g):
        r = res(g); return any(r[i] == r[i + 1] == r[i + 2] == '-' for i in range(len(r) - 2))
    def comeback(g, who):
        other = 'W' if who == 'L' else 'L'
        if winner(g) != who: return False
        sc = {'L': 0, 'W': 0}
        for x in res(g):
            if x in sc: sc[x] += 1
            if sc[other] > sc[who]: return True
        return False
    judge('ZJ2025A-104', G, {'A': lambda g: consec_win(g, 'L'), 'B': three_draws, 'C': lambda g: comeback(g, 'L'), 'D': lambda g: comeback(g, 'W')}, 'cannot', 'D',
          note=f"小李出法（去掉石头）恒为{sorted({tuple(sorted(a for a, b in g if a)) for g in G})}，小王恒为{sorted({tuple(sorted(b for a, b in g if b)) for g in G})}；小王获胜的对局中小李赢的场数={sorted({res(g).count('L') for g in G if winner(g) == 'W'})}")

def sc2025_84():
    P = '甲乙丙丁戊己庚'; M = []
    for v in product('JKL', repeat=7):          # J 就业 K 考研 L 留学
        if any(not 2 <= v.count(c) <= 3 for c in 'JKL'): continue
        X = dict(zip(P, v))
        if not imp(X['甲'] in 'JL' or X['丙'] in 'JL', X['乙'] == 'K' and X['戊'] == 'K'): continue
        if not imp(X['乙'] in 'JK' or X['丁'] in 'JK', X['己'] == 'L' and X['庚'] == 'L'): continue
        if not imp(X['戊'] in 'KL' or X['己'] in 'KL', X['乙'] == 'J' and X['丙'] == 'J'): continue
        M.append(X)
    liu = lambda X: ''.join(p for p in P if X[p] == 'L')
    # 选项“选择留学的同学有：X 和 Y”按“X、Y 都选择留学”判断（必然）；另按“留学名单恰为 X、Y”对照（可能）。
    pairs = {'A': '甲乙', 'B': '丙戊', 'C': '乙丁', 'D': '丁庚'}
    judge('SC2025-84', M, {k: (lambda pr: (lambda X: all(X[p] == 'L' for p in pr)))(pr) for k, pr in pairs.items()}, 'must', 'C',
          note=f"留学名单的可能={sorted({liu(X) for X in M})}；庚的去向={sorted({X['庚'] for X in M})}")
    reading('SC2025-84', '名单恰为这两人（问可能）', M, {k: (lambda pr: (lambda X: liu(X) == pr))(pr) for k, pr in pairs.items()}, 'can')

def gdxd2020sw_6():
    P = '甲乙丙丁'; games = list(combinations(P, 2)); M = []
    for r in product((0, 1, 2), repeat=6):      # 0: 前者胜  1: 平  2: 后者胜
        if r.count(1) != 1: continue
        pts = dict.fromkeys(P, 0); res = {}
        for (a, b), x in zip(games, r):
            if x == 0: pts[a] += 2; res[(a, b)] = 'W'; res[(b, a)] = 'L'
            elif x == 2: pts[b] += 2; res[(a, b)] = 'L'; res[(b, a)] = 'W'
            else: pts[a] += 1; pts[b] += 1; res[(a, b)] = res[(b, a)] = 'D'
        if pts == {'甲': 4, '乙': 3, '丙': 0, '丁': 5}: M.append(res)
    yi = lambda m: sorted(m[('乙', q)] for q in '甲丙丁')
    judge('GDXD2020SW-6', M, {'A': lambda m: m[('甲', '乙')] == 'W', 'B': lambda m: m[('乙', '丁')] == 'W', 'C': lambda m: m[('丁', '甲')] == 'W', 'D': lambda m: yi(m) == ['D', 'L', 'W']},
          'cannot', 'B', note=f"唯一赛果：乙丁={M[0][('乙', '丁')]}，甲乙={M[0][('甲', '乙')]}，丁甲={M[0][('丁', '甲')]}")

def gd2014x_84():
    P = '甲乙丙丁'; M = []
    for ph, pc, cam in product(product(B, repeat=4), repeat=3):
        if sum(ph) != 3 or sum(pc) != 2 or sum(cam) != 1: continue
        if sum(1 for i in range(4) if ph[i] and pc[i] and cam[i]) != 1: continue
        if any(not (ph[i] or pc[i] or cam[i]) for i in range(4)): continue
        if pc[0] != pc[1] or ph[1] != ph[2] or ph[2] == ph[3]: continue
        M.append(dict(ph=ph, pc=pc, cam=cam))
    judge('GD2014X-84', M, {k: (lambda i: (lambda m: m['cam'][i] == 1))(i) for i, k in enumerate('ABCD')}, 'must', 'C', note=str(M))

def gd2014x_82():
    P = ['赵', '钱', '孙', '李']; M = []
    knew = [{'孙', '李'}, {'钱', '李'}]                 # 赛前已相识的两对
    for order in permutations(P):
        r = {p: i + 1 for i, p in enumerate(order)}
        if {order[0], order[2]} in knew: continue        # 第一名与第三名这次比赛才认识
        if order[1] in ('孙', '李', '钱'): continue      # 第二名不打篮球（孙、李打）、不骑车（钱、李骑）
        if not r['赵'] < r['钱']: continue
        M.append(''.join(order))
    judge('GD2014X-82', M, {'A': lambda m: m == '孙赵钱李', 'B': lambda m: m == '李赵孙钱', 'C': lambda m: m == '李孙赵钱', 'D': lambda m: m == '孙李赵钱'}, 'must', 'A', note=str(M))

def gd2014z_85():
    # 姓 ∈ {莫,徐,刘,昌,其他}，年龄 ∈ {青年,中年,老年}，性别，专长 ∈ {会计,建筑,农业,其他}。每位村民听到的四项中恰有一项正确。
    heard = [('莫', '中', '女', '会计'), ('徐', '中', '男', '建筑'), ('刘', '青', '男', '农业'), ('昌', '青', '男', '建筑'), ('莫', '老', '男', '农业')]
    M = []
    for t in product(['莫', '徐', '刘', '昌', '他姓'], ['青', '中', '老'], ['男', '女'], ['会计', '建筑', '农业', '他长']):
        if all(sum(a == b for a, b in zip(t, h)) == 1 for h in heard): M.append(t)
    judge('GD2014Z-85', M, {'A': lambda t: t[0] == '刘' and t[1] == '青' and t[2] == '女', 'B': lambda t: t[0] == '莫' and t[1] == '老' and t[2] == '男',
                            'C': lambda t: t[3] == '会计', 'D': lambda t: t[3] == '建筑'}, 'must', 'D', note=str(M))

def zj2021a_106():
    P = '张王李赵'; M = []
    for books in product((1, 2, 3), repeat=4):
        for nums in product((1, 2, 3), repeat=4):
            Bk = dict(zip(P, books)); N = dict(zip(P, nums))
            if Bk['张'] == Bk['赵'] or N['张'] == N['赵']: continue
            if nums.count(1) != 1 or nums.count(2) != 2: continue
            if Bk['李'] != 3 or N['李'] != 3: continue
            if set(books) != {1, 2, 3} or Bk['王'] != 1 or Bk['赵'] != 1: continue
            M.append((Bk, N))
    judge('ZJ2021A-106', M, {'A': lambda m: m[0]['张'] == m[0]['李'], 'B': lambda m: m[1]['王'] == 2,
                             'C': lambda m: any(m[0][p] == 3 or m[1][p] == 3 for p in '张王赵'), 'D': lambda m: m[1]['赵'] == 2}, 'must', 'B', note=str(M))
    # 读法对照：（2）读成“至少 1 人选 1 个专题、至少 2 人选 2 个专题”
    M2 = []
    for books in product((1, 2, 3), repeat=4):
        for nums in product((1, 2, 3), repeat=4):
            Bk = dict(zip(P, books)); N = dict(zip(P, nums))
            if Bk['张'] == Bk['赵'] or N['张'] == N['赵'] or nums.count(1) < 1 or nums.count(2) < 2: continue
            if Bk['李'] != 3 or N['李'] != 3 or set(books) != {1, 2, 3} or Bk['王'] != 1 or Bk['赵'] != 1: continue
            M2.append((Bk, N))
    reading('ZJ2021A-106', '（2）按“至少”', M2, {'A': lambda m: m[0]['张'] == m[0]['李'], 'B': lambda m: m[1]['王'] == 2,
                                              'C': lambda m: any(m[0][p] == 3 or m[1][p] == 3 for p in '张王赵'), 'D': lambda m: m[1]['赵'] == 2}, 'must')

def gk2014_115():
    # 10 个柜：上级 U×1，本局 Bj×2，处室 C×3，基层 J×4。
    M = []
    for pos in set(permutations('UBBCCCJJJJ')):
        if pos[0] != 'C' or pos[9] != 'C' or pos[3] != 'B' or pos[4] != 'U': continue
        b = [i for i in range(10) if pos[i] == 'B']
        if b[1] - b[0] != 1: continue
        adj = [(pos[i], pos[i + 1]) for i in range(9)]
        if any(set(x) == {'J', 'B'} for x in adj) or any(set(x) == {'C', 'U'} for x in adj): continue
        M.append(''.join(pos))
    judge('GK2014-115', M, {'A': lambda m: m[5] == 'C', 'B': lambda m: m[6] == 'C', 'C': lambda m: m[1] == 'J', 'D': lambda m: m[8] == 'J'}, 'must', 'D', note=str(M))

def js2015a_65():
    ppl = '张王李赵周吴郑钱刘孙'
    segs = ['张王李赵周', '吴王张赵郑', '李钱张刘吴', '郑张王钱周']
    def matchings(rest):
        if not rest: yield []; return
        a = rest[0]
        for b in rest[1:]:
            r2 = [x for x in rest if x not in (a, b)]
            for m in matchings(r2): yield [frozenset((a, b))] + m
    M = []
    for m in matchings(list(ppl)):
        if all(all(sum(p in s for p in c) == 1 for c in m) for s in segs): M.append(frozenset(m))
    def opt(txt): return frozenset(frozenset(x) for x in txt.split('、'))
    opts = {'A': opt('李吴、周郑、赵钱、孙张、刘王'), 'B': opt('刘赵、钱王、孙李、郑张、周吴'), 'C': opt('孙张、李郑、吴周、刘王、赵钱'), 'D': opt('孙张、周郑、李吴、刘赵、王钱')}
    judge('JS2015A-65', M, {k: (lambda o: (lambda m: m == o))(o) for k, o in opts.items()}, 'must', 'C', note=str([sorted(''.join(sorted(c)) for c in m) for m in M]))

def sz2020sw_78():
    isl = ['巴厘', '塞舌尔', '塔希提', '塞班', '帕劳']; M = []
    for p in permutations(range(1, 6)):
        X = dict(zip(isl, p))
        say = [(X['巴厘'] == 4, X['塞舌尔'] == 5), (X['塞班'] == 2, X['塔希提'] == 5), (X['帕劳'] == 4, X['塞舌尔'] == 2), (X['巴厘'] == 3, X['塞班'] == 4), (X['塞舌尔'] == 5, X['巴厘'] == 1)]
        if all(a + b == 1 for a, b in say): M.append(p)
    judge('SZ2020SW-78', M, {'A': lambda p: p == (2, 5, 1, 3, 4), 'B': lambda p: p == (4, 1, 3, 5, 2), 'C': lambda p: p == (4, 2, 3, 5, 1), 'D': lambda p: p == (3, 5, 1, 2, 4)}, 'must', 'D', note=str(M))

def js2016a_95():
    T = '甲乙丙丁戊'; games = list(combinations(T, 2)); M = []
    for r in product((0, 1, 2), repeat=10):
        pts = dict.fromkeys(T, 0); w = dict.fromkeys(T, 0); res = {}
        for (a, b), x in zip(games, r):
            if x == 0: pts[a] += 3; w[a] += 1; res[(a, b)] = 'W'; res[(b, a)] = 'L'
            elif x == 2: pts[b] += 3; w[b] += 1; res[(a, b)] = 'L'; res[(b, a)] = 'W'
            else: pts[a] += 1; pts[b] += 1; res[(a, b)] = res[(b, a)] = 'D'
        if len(set(pts.values())) != 5: continue
        if w['乙'] != 3 or res[('乙', '甲')] != 'L': continue
        rank = sorted(T, key=lambda t: -pts[t]); M.append(set(rank[:2]))
    judge('JS2016A-95', M, {k: (lambda t: (lambda q: t in q))(t) for k, t in zip('ABCD', '甲乙丙戊')}, 'must', 'B', note=f'出线组合={sorted({"".join(sorted(q)) for q in M})}')

def sz2024_43():
    # 按原图读出的 11 种模具规格（L 长度, W 宽度）——见 moulds；小李知 L，小范知 W。
    moulds = [(10, 6), (10, 8), (15, 10), (15, 12), (15, 14), (20, 16), (25, 16), (30, 12), (30, 16), (30, 18), (35, 16)]
    L = lambda m: m[0]; W = lambda m: m[1]
    s0 = list(moulds)
    # ① 两人同时表示不知道：L、W 都不唯一
    s1 = [m for m in s0 if sum(L(x) == L(m) for x in s0) > 1 and sum(W(x) == W(m) for x in s0) > 1]
    # ② 小范（知 W）说现在知道了：在 s1 中 W 唯一
    s2 = [m for m in s1 if sum(W(x) == W(m) for x in s1) == 1]
    # ③ 小李（知 L）说也知道了：在 s2 中 L 唯一
    s3 = [m for m in s2 if sum(L(x) == L(m) for x in s2) == 1]
    opts = {'A': (30, 12), 'B': (20, 12), 'C': (30, 16), 'D': (15, 12)}
    record('SZ2024-43', ''.join(k for k, v in opts.items() if [v] == s3), 'C', f's1={s1} s2={s2} s3={s3}')


# =====================================================================================
# D12-C3 组合（一拖 n）
# =====================================================================================
def gk2023d_set():
    D = ['财', '研', '人', '后', '法', '销']; M = []
    for s in product(D, repeat=6):
        if any(s.count(d) > 2 for d in D): continue            # 每个部门只推荐 2 人，每人至多值一天
        if s[1] == '法' or s[3] == '法': continue
        if any(d == '后' and not (i + 1 < 6 and s[i + 1] == '法') for i, d in enumerate(s)): continue
        if any(d == '研' and not (i + 1 < 6 and s[i + 1] == '后') for i, d in enumerate(s)): continue
        M.append(s)
    seq = lambda txt: tuple(txt)
    judge('GK2023D-106', M, {'A': lambda s: s == seq('财人后法财人'), 'B': lambda s: s == seq('销财法人财销'), 'C': lambda s: s == seq('人财法研法后'), 'D': lambda s: s == seq('法销人后财销')}, 'can', 'B')
    hq = sorted({i + 1 for s in M for i, d in enumerate(s) if d == '后'})
    o107 = {'A': [2, 4, 5], 'B': [1, 3, 5], 'C': [2, 6], 'D': [1, 3]}
    record('GK2023D-107', ''.join(k for k, v in o107.items() if v == hq), 'A', f'后勤部门可以值班的日子={hq}')
    S = [s for s in M if s.count('后') == 2]
    judge('GK2023D-108', S, {'A': lambda s: s[0] == '研', 'B': lambda s: s[5] == '人', 'C': lambda s: s[2] == '财', 'D': lambda s: s[4] == '法'}, 'cannot', 'C',
          note=f"后勤两天的位置={sorted({tuple(i + 1 for i, d in enumerate(s) if d == '后') for s in S})}")
    S = [s for s in M if s[2] == '财' and s[4] == '财']
    judge('GK2023D-109', S, {'A': lambda s: (s[0], s[5]) == ('后', '法'), 'B': lambda s: (s[0], s[5]) == ('法', '销'), 'C': lambda s: (s[0], s[5]) == ('财', '销'), 'D': lambda s: (s[0], s[5]) == ('研', '人')}, 'can', 'B')
    S = [s for s in M if '财' not in s and '后' not in s]
    judge('GK2023D-110', S, {'A': lambda s: s[3] == '销', 'B': lambda s: s[4] == '法', 'C': lambda s: s[1] in ('销', '人'), 'D': lambda s: s[2] in ('法', '人')}, 'must', 'C',
          note=f"此时可用部门只有人事、销售、法务（研发须接后勤，也排不了）：{sorted({''.join(s) for s in S})[:6]}…")
    print(f'   GK2023D base models = {len(M)}')

def js2017a_set():
    teas = ['黑', '白', '黄', '绿', '红']; M = []
    for p in permutations(range(1, 6)):
        X = dict(zip(teas, p))
        if X['黄'] not in (2, 4): continue
        if not imp(X['白'] == 3, X['绿'] == 5): continue
        if (X['红'] in (1, 2)) != (X['黑'] == 5): continue
        M.append(X)
    box = lambda t: {k: (lambda n: (lambda X: X[t] == n))(n) for k, n in zip('ABCD', (1, 2, 3, 4))}
    judge('JS2017A-98', [X for X in M if X['白'] == 3], box('黑'), 'must', 'A')
    judge('JS2017A-99', [X for X in M if X['绿'] == 2 and X['白'] != 1], box('黑'), 'must', 'A')
    judge('JS2017A-100', [X for X in M if X['黑'] == 5 and X['黄'] != 4], box('绿'), 'must', 'C')
    print(f'   JS2017A base models = {len(M)}')

def js2015a_set():
    # 王刚 W、赵虎 Z、李亮 L；特征：单身 d、乒乓 p、北方 n、硕士 s。
    # 读法：cnt ∈ {exact: 每个特征恰有两人, atleast: 至少两人}；cond ∈ {joint: “都是…则都…”整体作前后件, dist: 逐人理解}
    ppl = 'WZL'
    def models(cnt, cond):
        M = []
        for bits in product(B, repeat=12):
            X = {(p, t): bits[i * 4 + j] for i, p in enumerate(ppl) for j, t in enumerate('dpns')}
            n = {t: sum(X[(p, t)] for p in ppl) for t in 'dpns'}
            if any((n[t] != 2) if cnt == 'exact' else (n[t] < 2) for t in 'dpns'): continue
            if any(sum(X[(p, t)] for t in 'dpns') > 3 for p in ppl): continue
            if cond == 'joint':
                if not imp(X[('W', 's')] and X[('L', 's')], X[('W', 'n')] and X[('L', 'n')]): continue
                if not imp(X[('Z', 'p')] and X[('L', 'p')], X[('Z', 'd')] and X[('L', 'd')]): continue
            else:
                if not (imp(X[('W', 's')], X[('W', 'n')]) and imp(X[('L', 's')], X[('L', 'n')])): continue
                if not (imp(X[('Z', 'p')], X[('Z', 'd')]) and imp(X[('L', 'p')], X[('L', 'd')])): continue
            M.append(X)
        return M
    o69 = {'A': lambda X: X[('W', 'd')], 'B': lambda X: X[('Z', 's')], 'C': lambda X: X[('L', 'p')], 'D': lambda X: X[('W', 'n')]}
    o70 = {'A': lambda X: X[('W', 'd')], 'B': lambda X: X[('W', 'p')], 'C': lambda X: X[('Z', 's')], 'D': lambda X: X[('L', 'n')]}
    M = models('exact', 'joint')
    judge('JS2015A-69', [X for X in M if imp(X[('W', 'n')], X[('W', 'd')])], o69, 'must', 'B')
    judge('JS2015A-70', [X for X in M if imp(X[('Z', 'd')], X[('W', 'd')])], o70, 'notmust', 'D')
    print(f'   JS2015A base models (恰两人, 整体条件) = {len(M)}')
    for cnt, cond in (('atleast', 'joint'), ('exact', 'dist'), ('atleast', 'dist')):
        M2 = models(cnt, cond)
        reading('JS2015A-69', f'{cnt},{cond}', [X for X in M2 if imp(X[('W', 'n')], X[('W', 'd')])], o69, 'must')
        reading('JS2015A-70', f'{cnt},{cond}', [X for X in M2 if imp(X[('Z', 'd')], X[('W', 'd')])], o70, 'notmust')

def js2021a_set():
    # 6 条隧道自南向北排成一列（位置 1=最南 … 6=最北）。
    T = ['长川', '大美', '青山', '绿水', '彩石', '白玉']; M = []
    for p in permutations(range(1, 7)):
        X = dict(zip(T, p))
        if X['白玉'] != X['彩石'] + 1: continue                       # 白玉在彩石北边并相邻
        if not (X['白玉'] < X['大美'] and X['大美'] - X['白玉'] >= 2): continue   # 白玉在大美南边且不相邻
        if abs(X['长川'] - X['青山']) != 2: continue                  # 之间隔一条
        M.append(X)
    judge('JS2021A-99', M, {'A': lambda X: X['长川'] == 1, 'B': lambda X: X['绿水'] == 6, 'C': lambda X: abs(X['彩石'] - X['青山']) == 2, 'D': lambda X: abs(X['白玉'] - X['大美']) == 2}, 'cannot', 'A',
          note=str([''.join(k[0] for k in sorted(X, key=X.get)) for X in M]))
    S = [X for X in M if abs(X['绿水'] - X['白玉']) == 1]
    judge('JS2021A-100', S, {'A': lambda X: X['彩石'] == 2, 'B': lambda X: X['大美'] == 5, 'C': lambda X: X['长川'] == 4, 'D': lambda X: X['青山'] == 3}, 'must', 'B',
          note=str([''.join(k[0] for k in sorted(X, key=X.get)) for X in S]))


# =====================================================================================
# 追加：广东 2021 县级卷（扫描件）两题、江苏 2019 排序题
# =====================================================================================
def gd2021x_67():
    flowers = ['玫瑰', '月季', '牡丹', '其他']; M = []
    for f in flowers:
        g = {'甲': [f == '月季', f != '玫瑰'], '乙': [f != '月季', f == '玫瑰'], '丙': [f != '月季', f != '牡丹']}
        if sorted(sum(v) for v in g.values()) == [0, 1, 2]: M.append(f)
    judge('GD2021X-67', M, {k: (lambda x: (lambda f: f == x))(x) for k, x in zip('ABCD', flowers)}, 'must', 'B', note=str(M))

def gd2021x_70():
    # 绿萝 L、罗汉松 S、文竹 W、橡皮树 X、虎尾兰 H。①“购买绿萝、罗汉松中的一种”按“恰好一种”（原解析同）；另按“至多一种”“至少一种”对照。
    opts = {'A': lambda m: m['H'], 'B': lambda m: m['X'], 'C': lambda m: m['S'] or m['W'], 'D': lambda m: sum(m.values()) >= 3}
    def models(rd):
        M = []
        for v in product(B, repeat=5):
            m = dict(zip('LSWXH', v)); n = m['L'] + m['S']
            if not {'exact': n == 1, 'atmost': n <= 1, 'atleast': n >= 1}[rd]: continue
            if not (m['W'] or m['L'] or m['X']): continue
            if m['S'] + m['X'] + m['H'] < 2: continue
            if not imp(m['S'], not m['W']): continue
            M.append(m)
        return M
    M = models('exact')
    judge('GD2021X-70', M, opts, 'must', 'B', note=str([''.join(k for k in 'LSWXH' if m[k]) for m in M]))
    reading('GD2021X-70', '①=至多一种', models('atmost'), opts, 'must')
    reading('GD2021X-70', '①=至少一种', models('atleast'), opts, 'must')

def js2019a_95():
    S = ['钟山', '长江', '梅园', '星海']; M = []
    for p in permutations(range(1, 5)):
        X = dict(zip(S, p))
        if not imp(X['钟山'] == 3, X['梅园'] == 1): continue
        if not imp(X['长江'] not in (1, 2), X['钟山'] == 3): continue
        if abs(X['钟山'] - X['梅园']) != 1 or abs(X['钟山'] - X['长江']) == 1: continue
        M.append(X)
    judge('JS2019A-95', M, {'A': lambda X: X['钟山'] in (1, 4), 'B': lambda X: X['长江'] in (2, 3), 'C': lambda X: X['梅园'] in (2, 4), 'D': lambda X: X['星海'] in (1, 3)}, 'must', 'A', note=str(M))

# =====================================================================================
# D12-S1 / S2 科学推理（可计算项复算；纯知识项只在答案册逐项说理）
# =====================================================================================
def gd2016z_63():
    # 蜡球密度 0.9，液体密度由 1.0（水）逐渐降到 0.8（接近酒精）。逐步记录“相对上一步的变化”。
    rho_wax, V, g = Fr(9, 10), Fr(1), Fr(10)
    G = rho_wax * V * g
    seen = set(); prev = None
    for k in range(0, 201):
        rho = Fr(1) - Fr(k, 1000)                      # 1.000 → 0.800
        if rho > rho_wax: state, F, Vd = '漂浮', G, G / (rho * g)
        elif rho == rho_wax: state, F, Vd = '悬浮', G, V
        else: state, F, Vd = '沉底', rho * g * V, V
        if prev:
            dF = '增大' if F > prev[1] else ('不变' if F == prev[1] else '变小')
            deeper = Vd > prev[2]
            if state == '漂浮' and deeper: seen.add(('向下沉一些', dF))
            if state == '悬浮': seen.add(('悬浮', dF))
            if state == '沉底': seen.add(('沉到杯底', dF))
        prev = (state, F, Vd)
    opts = {'A': ('向下沉一些', '增大'), 'B': ('向下沉一些', '不变'), 'C': ('悬浮', '不变'), 'D': ('沉到杯底', '变小')}
    record('GD2016Z-63', ''.join(k for k, v in opts.items() if v not in seen), 'A', f'加酒精过程中出现过的情形={sorted(seen)}')

def gd2018_64():
    # 两箱质量均为 m，坡角 30°，随车匀速（平衡）。B 在上坡一侧、A 在下坡一侧；两箱之间的挤压力 T（B 压 A，沿斜面向下）题干无法确定，取 0≤T≤mg·sin30° 逐一检验。
    m, g = 1.0, 10.0; th = math.radians(30); res = []
    for i in range(0, 51):
        T = m * g * math.sin(th) * i / 50
        fA = m * g * math.sin(th) + T; fB = m * g * math.sin(th) - T          # 沿斜面向上的静摩擦力
        NA = NB = m * g * math.cos(th)
        res.append({'A': False,                                   # B 所受合外力为 0，不存在“沿斜面向上”的合外力
                    'B': abs(T - 0.5 * m * g) < 1e-9, 'C': fA > fB + 1e-9, 'D': abs(NA - NB) < 1e-9})
    st = {k: ('ALL' if all(r[k] for r in res) else 'SOME' if any(r[k] for r in res) else 'NONE') for k in 'ABCD'}
    record('GD2018-64', ''.join(k for k, v in st.items() if v == 'ALL'), 'D', f'对 T∈[0, mg·sin30°] 逐一检验：{st}（B、C 只在两箱恰好挤紧的特殊情形才成立，不能断定）')

def gd2016z_68():
    v_board = -1.0; v_A = 0.0                         # 木板向左（负方向）运动；木块被测力计拉住，相对地面静止
    rel = v_A - v_board                               # 木块相对木板的速度 >0：向右
    f_dir = '向左' if rel > 0 else '向右'              # 滑动摩擦力与相对运动方向相反
    mu, N = 0.3, 10.0
    readings = {abs(v): mu * N for v in (-0.5, -1.0, -2.0)}     # 滑动摩擦力与速度无关
    st = {'A': rel == 0, 'B': v_A != 0, 'C': f_dir == '向左', 'D': len(set(readings.values())) > 1}
    record('GD2016Z-68', ''.join(k for k, v in st.items() if v), 'C', f'木块相对木板{"向右" if rel > 0 else "向左"}滑动→滑动摩擦力{f_dir}；不同拉动速度下示数={sorted(set(readings.values()))}')

def gd2021z_74():
    m, g, vx, vy = 1.0, 10.0, 6.0, 8.0; T = 2 * vy / g
    ts = [T * i / 200 for i in range(201)]
    Ek = [0.5 * m * (vx ** 2 + (vy - g * t) ** 2) for t in ts]
    i_min = Ek.index(min(Ek))
    shape = dict(start_zero=Ek[0] == 0, dec_then_inc=all(Ek[i] > Ek[i + 1] for i in range(i_min)) and all(Ek[i] < Ek[i + 1] for i in range(i_min, 200)),
                 min_positive=min(Ek) > 0, end_equals_start=abs(Ek[-1] - Ek[0]) < 1e-9)
    # 选项图形（按原图）：A 从 0 升到最大再回到 0；B 先减小后增大、最小值不为 0；C 从 0 起直线上升；D 从 0 起折线上升
    opts = {'A': dict(start_zero=True, dec_then_inc=False), 'B': dict(start_zero=False, dec_then_inc=True, min_positive=True), 'C': dict(start_zero=True, dec_then_inc=False), 'D': dict(start_zero=True, dec_then_inc=False)}
    record('GD2021Z-74', ''.join(k for k, o in opts.items() if all(shape[a] == b for a, b in o.items())), 'B', f'Ek(t)=½m[vx²+(vy−gt)²]：{shape}，最小值={min(Ek):.1f}（最高点仍有水平速度）')

def gd2020x_84():
    # 按原图读点（像素坐标，y 向下）：A(505,385) B(612,280) C(722,220)，O—A、C—D 两段水平。
    A, Bp, C = (505, 385), (612, 280), (722, 220)
    k1 = (A[1] - Bp[1]) / (Bp[0] - A[0]); k2 = (Bp[1] - C[1]) / (C[0] - Bp[0])
    v = [0, k1, k2, 0]                                # O—A、A—B、B—C、C—D 四段的速度（位移图线的斜率）
    pattern = ('0', '高', '低', '0') if v[1] > v[2] > 0 else ('0', '低', '高', '0')
    # 选项图形（按原图）：A 先低后高再匀减速到 0；B 光滑曲线先增后减；C 先高后低（两段水平线）再为 0；D 速度先匀加速、再缓慢增加、最后不变
    opts = {'A': ('低', '高', '匀减速'), 'B': ('曲线',), 'C': ('高', '低', '0'), 'D': ('匀加速', '匀加速', '不变')}
    record('GD2020X-84', ''.join(k for k, o in opts.items() if o == pattern[1:]), 'C', f'斜率 AB={k1:.2f} > BC={k2:.2f} > 0，CD=0 → 速度依次为{pattern}')

def gd2021x_80():
    # 滑片向右推 → 接入电路的是“滑片到右端”一段，阻值 Rx = R0(1−x)，x 从 0.1 增到 0.9。电源电压 U、定值电阻 R。
    U, R, R0 = 6.0, 10.0, 20.0; xs = [0.1 * i for i in range(1, 10)]
    Rx = lambda x: R0 * (1 - x)
    meter = {'A': lambda x: U / Rx(x),                    # 电流表与变阻器串联在一条支路上（定值电阻另成一条支路）
             'B': lambda x: U,                            # 电压表直接接在电源两端
             'C': lambda x: U / R + U / Rx(x),            # 电流表在干路
             'D': lambda x: U * R / (R + Rx(x))}          # 定值电阻与变阻器串联，电压表测定值电阻
    inc = {k: all(f(xs[i + 1]) > f(xs[i]) + 1e-12 for i in range(len(xs) - 1)) for k, f in meter.items()}
    record('GD2021X-80', ''.join(k for k, v in inc.items() if not v), 'B', f'滑块右移时示数是否随之增大：{inc}')

def gd2019x_62():
    U, R = 220.0, 484.0; rows = []
    for n in range(1, 5): rows.append(dict(n=n, I_each=U / R, U_each=U, I_total=n * U / R, P_each=U * U / R))
    inc = lambda key: all(rows[i + 1][key] > rows[i][key] for i in range(3)); dec = lambda key: all(rows[i + 1][key] < rows[i][key] for i in range(3))
    st = {'A': inc('I_each'), 'B': dec('U_each'), 'C': inc('I_total'), 'D': dec('P_each')}
    record('GD2019X-62', ''.join(k for k, v in st.items() if v), 'C', f"干路电流={[round(r['I_total'], 3) for r in rows]}，每盏灯的电流、电压、功率都不变")

def gd2022x_77():
    # 俯视图（按原图读像素坐标，x 向右、y 向下）：镜面为竖直线 x=xm；球心 ball；人的位置 P、视线方向 d。
    panels = {'A': dict(xm=212, ball=(288, 546), P=(258, 655), d=(-26, -48)), 'B': dict(xm=529, ball=(591, 573), P=(650, 573), d=(-28, 38)),
              'C': dict(xm=846, ball=(901, 578), P=(955, 637), d=(-1, 0)), 'D': dict(xm=1163, ball=(1221, 560), P=(1288, 499), d=(-1, 0))}
    def bearing(P, d, T):
        # 目标相对视线的方位角（度）：负=偏左，正=偏右。先把 y 轴翻成向上。
        dx, dy = d[0], -d[1]; vx, vy = T[0] - P[0], -(T[1] - P[1])
        ang = math.degrees(math.atan2(dx * vy - dy * vx, dx * vx + dy * vy))     # 逆时针为正＝偏左
        return -ang
    def check(pn, jitter=(0, 0, 0, 0)):
        xm = pn['xm']; ball = (pn['ball'][0] + jitter[0], pn['ball'][1] + jitter[1]); P = (pn['P'][0] + jitter[2], pn['P'][1] + jitter[3])
        img = (2 * xm - ball[0], ball[1])
        b1, b2 = bearing(P, pn['d'], ball), bearing(P, pn['d'], img)
        d1 = math.hypot(ball[0] - P[0], ball[1] - P[1]); d2 = math.hypot(img[0] - P[0], img[1] - P[1])
        r_ball = 17                                                           # 选项图中“球”的半径（像素）
        visible = abs(b1) < 60 and abs(b2) < 60 and abs(b1 - b2) > math.degrees(math.asin(min(1.0, r_ball / d1)))   # 两者都在视野内、且像没有被球挡住（方位差大于球的视半径）
        return visible and b1 < b2 and d1 < d2, (round(b1, 1), round(b2, 1))   # 题图：球（大、近）在左，像（小、远）在右
    random.seed(11); ok = {}; base = {}
    for k, pn in panels.items():
        r0, base[k] = check(pn)
        ok[k] = r0 and all(check(pn, tuple(random.uniform(-8, 8) for _ in range(4)))[0] for _ in range(300))
        if not r0: assert not any(check(pn, tuple(random.uniform(-8, 8) for _ in range(4)))[0] for _ in range(300)), k
    record('GD2022X-77', ''.join(k for k, v in ok.items() if v), 'D', f'（球方位角, 像方位角；负=偏左）{base}；坐标各抖动±8像素300次结论不变')

def gd2020z_75():
    # 甲在 1000hPa 等压线的最低点，高压（1008）在其上方：气压梯度力由高压指向低压、垂直于等压线，在甲处竖直向下（y 轴向上为正）。
    pgf = (0.0, -1.0)
    def rotate_cw(v, deg):
        a = math.radians(deg); return (v[0] * math.cos(a) + v[1] * math.sin(a), -v[0] * math.sin(a) + v[1] * math.cos(a))
    winds = [rotate_cw(pgf, a) for a in range(10, 90, 5)]          # 北半球向右偏：顺时针转过 0—90° 之间的某个角度
    sector = lambda v: v[0] < 0 and v[1] <= 0                       # 允许的风向扇区：指向左下（西南方向一侧）
    assert all(sector(w) for w in winds)
    arrows = {'A': (-33, -10), 'B': (38, -9), 'C': (24, 17), 'D': (-18, 22)}      # 四个选项箭头方向（按原图读，已换成 y 向上）
    record('GD2020Z-75', ''.join(k for k, v in arrows.items() if sector(v)), 'A', '气压梯度力向下（由 1008 指向 1000），北半球右偏后指向左下；四个箭头分别指向 左略偏下/右略偏下/右上/左上')

def gd2020z_67():
    # 雪线高度的变化方向：变暖 → 上移(+1)，变冷 → 下移(−1)；降雪量增加 → 下移(−1)，减少 → 上移(+1)。两个因素同向时结果确定，反向时两种都可能。
    opts = {'A': (+1, -1, '上移'), 'B': (+1, +1, '上移'), 'C': (-1, +1, '下移'), 'D': (-1, -1, '上移')}
    def possible(t, s):
        return {'上移'} if t > 0 and s > 0 else {'下移'} if t < 0 and s < 0 else {'上移', '下移'}
    res = {k: (obs in possible(t, s)) for k, (t, s, obs) in opts.items()}
    record('GD2020Z-67', ''.join(k for k, v in res.items() if not v), 'D', f'各选项所述现象能否出现：{res}')

def v_work_graph():
    # 改编（母题 GD2024-68）：F 依次为 2N(0–2s，静止)、4N(2–4s，匀加速)、3N(4–6s，匀速)、1N(6–7s，匀减速，7s 末恰好停下)。
    for m in (Fr(1, 2), Fr(1), Fr(3), Fr(7, 2)):
        f = Fr(3)                                              # 匀速段：滑动摩擦力 = 拉力 = 3 N
        segs = [(Fr(4), Fr(2)), (Fr(3), Fr(2)), (Fr(1), Fr(1))]     # (F, 时长)：2–4s、4–6s、6–7s
        v = Fr(0); WF = []; Wf = []; disp = []
        for F, dt in segs:
            a = (F - f) / m; s = v * dt + a * dt * dt / 2; v = v + a * dt
            assert s > 0
            WF.append(F * s); Wf.append(-f * s); disp.append(s)
        assert v == 0                                          # 7 s 末恰好停下，题设自洽
        f_static = Fr(2)                                       # 0–2 s 静止：静摩擦力 = 拉力 = 2 N
        st = {'A': f_static == 3, 'B': Wf[0] == Wf[2], 'C': sum(WF) == -sum(Wf), 'D': WF[2] < 0}
        ans = ''.join(k for k, val in st.items() if val)
        assert ans == 'C', (m, st)
    record('PD4C-VS1(拉力与摩擦力做功)', ans, 'C', f'm 任取：位移比 加速:匀速:减速={disp[0] / disp[2]}:{disp[1] / disp[2]}:1，摩擦力做功 {Wf[0]} J 对 {Wf[2]} J（m={m}kg），拉力总功={sum(WF)} J=克服摩擦力做功')
    # 记忆检验：母题（减速段也是 2 s、F=2N）中两段摩擦力做功相等
    v = Fr(0); m = Fr(1); f = Fr(3); W = []
    for F, dt in [(Fr(4), Fr(2)), (Fr(3), Fr(2)), (Fr(2), Fr(2))]:
        a = (F - f) / m; s = v * dt + a * dt * dt / 2; v += a * dt; W.append(-f * s)
    assert v == 0 and W[0] == W[2]
    print('   memory check: 母题（2–4s 加速、6–8s 减速）两段摩擦力做功相等；本题减速段只有 1 s，位移减半 → 记得母题会误选 B')

SCI = [gd2016z_63, gd2018_64, gd2016z_68, gd2021z_74, gd2020x_84, gd2021x_80, gd2019x_62, gd2022x_77, v_work_graph, gd2020z_75, gd2020z_67]

# =====================================================================================
# 与 questions.jsonl 交叉核对
# =====================================================================================
def crosscheck():
    import json, os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'questions.jsonl')
    if not os.path.exists(path):
        print('questions.jsonl not found, crosscheck skipped'); return
    rows = [json.loads(l) for l in open(path)]
    bad = 0; n_prog = 0; qual = []
    for r in rows:
        v = r.get('verify') or ''
        if '::' not in v: qual.append(r['id']); continue
        k = v.split('::', 1)[1]
        if k not in RESULTS: bad += 1; print('XX missing result', r['id'], k); continue
        n_prog += 1
        if RESULTS[k] != r['checked_answer']: bad += 1; print('XX', r['id'], k, RESULTS[k], r['checked_answer'])
    mism = [r['id'] for r in rows if r.get('source_answer') and r['source_answer'] != r['checked_answer']]
    if mism: bad += 1
    print(f'crosscheck: {len(rows)} items; {n_prog} program-verified, {len(qual)} qualitative ({", ".join(qual)}); source/checked mismatches: {mism or "none"}')
    assert bad == 0

COND = [gk2016f_111, js2021a_97, gd2021x_70, sd2023_68, gk2017f_113, hb2022_110, gd2021x_67, sd2021_71, js2023a_103, sz2020sw_80]
COMBO = [gdxd2020sw_6, zj2021a_106, js2019a_95, gd2014z_85, gk2014_115, sc2025_84, zj2025a_104, sz2024_43, sz20201_33, sz20201_38]
SETS = [gk2023d_set, js2017a_set, js2015a_set]
# 已穷举、本日未用的备选（python3 -I verify_d12.py --reserve 时一并运行；结果不参与 crosscheck）
RESERVE = [gdxd2020sw_24, gd2014x_84, gd2014x_82, js2015a_65, sz2020sw_78, js2016a_95, js2021a_set]

if __name__ == '__main__':
    for f in COND + COMBO + SETS + SCI: f()
    n_main = len(RESULTS)
    crosscheck()
    if '--reserve' in sys.argv:
        print('\n--- reserve (not in today\'s set) ---')
        for f in RESERVE: f()
    print(f'\n{n_main} checks passed')
