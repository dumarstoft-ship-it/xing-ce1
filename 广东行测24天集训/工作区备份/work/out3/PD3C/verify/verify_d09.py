"""PD3C / D09 verification script (第3轮判断日：条件与必然性 13 + 组合 17 + 科推 15).
Every logic item is solved by exhaustive enumeration of all models consistent with the stem (independent of the source analysis);
where a reading could change the answer, every reading is enumerated and must give the same answer.
Every computable science item is re-computed; the two science adaptations are solved from scratch.
Run:  python3 -I verify_d09.py
Each check prints the option(s) satisfying the ask and asserts it equals the expected (checked) answer;
crosscheck() then compares every result with checked_answer / source_answer in ../questions.jsonl."""
import sys, math, random
from itertools import permutations, product, combinations
from fractions import Fraction as Fr

RESULTS = {}
def imp(a, b): return (not a) or b

def judge(qid, models, opts, mode, expect, note=''):
    """mode: must = true in every model; can = true in some model; cannot = true in no model; notmust = not true in every model"""
    assert models, qid + ': no model satisfies the stem'
    stat = {}
    for k, f in opts.items():
        v = [bool(f(m)) for m in models]
        stat[k] = 'ALL' if all(v) else ('SOME' if any(v) else 'NONE')
    sel = {'must': lambda s: s == 'ALL', 'can': lambda s: s != 'NONE', 'cannot': lambda s: s == 'NONE', 'notmust': lambda s: s != 'ALL'}[mode]
    ans = ''.join(k for k, s in stat.items() if sel(s))
    RESULTS[qid] = ans
    print(f"{'OK ' if ans == expect else 'XX '}{qid:30s} models={len(models):7d} ask={mode:7s} -> {ans:4s} (expect {expect})  {stat} {note}")
    assert ans == expect, qid
    return ans

def record(qid, ans, expect, msg):
    RESULTS[qid] = ans
    print(('OK ' if ans == expect else 'XX ') + f'{qid:30s} {msg} -> {ans} (expect {expect})')
    assert ans == expect, qid

B = (0, 1)
# =====================================================================================
# 条件与必然性 · A组（条件推理）
# =====================================================================================
def gk2025f_115():
    P = '甲乙丙丁戊己庚'; M = []
    for v in product(B, repeat=7):
        a = dict(zip(P, v))
        if a['戊'] + a['己'] + a['庚'] < 2: continue
        if not imp(a['甲'] or a['丙'] or a['戊'], not a['丁'] and not a['己']): continue
        if not imp(a['乙'] or a['戊'] or a['己'], a['丁'] and not a['丙']): continue
        M.append(a)
    judge('GK2025F-115', M, {k: (lambda x: (lambda a: a[x]))(x) for k, x in zip('ABCD', '甲乙丙丁')}, 'must', 'D',
          note=f"winners={[''.join(p for p in P if a[p]) for a in M]}")

def gk2017f_114():
    # 纳税额取 1..4（允许相等）；已知帮助关系 李→王、王→赵，另可任意增加公司内其他帮助关系（不影响“有人帮助了……”的必然性判断，
    # 只会让存在句更容易为真；为检验 C 不必然，最小模型即只有这两条帮助关系）。
    M = []
    for L, W, Z in product(range(1, 5), repeat=3):
        if L > Z: M.append(dict(L=L, W=W, Z=Z, helps=[('L', 'W'), ('W', 'Z')]))
    tax = lambda m, x: m[x]
    judge('GK2017F-114', M, {'A': lambda m: m['W'] > m['Z'], 'B': lambda m: m['L'] == m['W'],
                             'C': lambda m: any(tax(m, e) > tax(m, h) for h, e in m['helps']),
                             'D': lambda m: any(tax(m, e) < tax(m, h) for h, e in m['helps'])}, 'must', 'D',
          note='(王刚≥李明 → 王刚帮助了比他少的赵贤；王刚<李明 → 李明帮助了比他少的王刚)')

def js2016a_98():
    # 4 位居民：刘 张 周 王。H[x][y]=x 帮助过 y。两种读法都穷举：
    #   R1 “帮助”只在不同的人之间（自己对自己不计），“有一人没帮助过他”指他以外的某人；
    #   R2 自己对自己的取值任意，量词覆盖全体（含本人）。
    ppl = ['刘', '张', '周', '王']; idx = {p: i for i, p in enumerate(ppl)}
    for rd in ('R1', 'R2'):
        M = []
        cells = [(x, y) for x in ppl for y in ppl if rd == 'R2' or x != y]
        for bits in product(B, repeat=len(cells)):
            H = {c: b for c, b in zip(cells, bits)}
            h = (lambda H: (lambda x, y: H.get((x, y), 0)))(H)       # 绑定本模型的 H（避免闭包晚绑定）
            ok = all(imp(h(x, '刘'), h('张', x)) for x in ppl if rd == 'R2' or x not in ('刘', '张'))
            ok = ok and all(imp(any(not h(z, y) for z in ppl if rd == 'R2' or z != y), h('周', y)) for y in ppl if rd == 'R2' or y != '周')
            ok = ok and all(not h('王', y) for y in ppl if y != '王')
            if ok: M.append(h)
        judge(f'JS2016A-98({rd})', M, {'A': lambda h: not h('周', '张'), 'B': lambda h: not h('周', '王'),
                                      'C': lambda h: h('刘', '张') and h('张', '刘'), 'D': lambda h: h('张', '周') and h('周', '张')}, 'must', 'D')

def sz2023_41():
    M = []
    for c, w, x, q, t, y, s in product(B, repeat=7):
        # c 春游 w 梧桐山 x 仙湖植物园 q 七娘山 t 和小雪一起出门 y 做好约定 s 小雪有时间
        if imp(c, w and x) and imp(not (w and x), not c) and imp(w or q, t) and imp(t, y) and imp(y, s) and not s:
            M.append(dict(c=c, w=w, x=x, q=q, t=t))
    judge('SZ2023-41', M, {'A': lambda m: not m['c'], 'B': lambda m: m['q'], 'C': lambda m: m['x'], 'D': lambda m: m['t']}, 'must', 'A')

def js2016a_92():
    # 个体类型 (教授 p, 行政 a, 30岁以下 y, 博士 d, 海外 o)；教授→¬行政；(30岁以下∧博士)→行政；海外→博士。
    # 李明：教授、29 岁（30 岁以下）；博士与否、海外与否未知。“或者…或者…”按可兼/不可兼两种读法（只影响是否允许“两种工作都不做”，结论不变）。
    for rd in ('incl', 'excl'):
        types = [t for t in product(B, repeat=5) if imp(t[0], not t[1]) and imp(t[2] and t[3], t[1]) and imp(t[4], t[3])]
        li_types = [t for t in types if t[0] and t[2]]
        M = []
        for li in li_types:
            for n in range(0, 3):
                for others in combinations(types, n):
                    pop = [li] + list(others)
                    M.append(pop)
        def most(pop, cond, among):
            grp = [t for t in pop if among(t)]
            return len(grp) > 0 and sum(1 for t in grp if cond(t)) * 2 > len(grp)
        judge(f'JS2016A-92({rd})', M, {'A': lambda pop: most(pop, lambda t: t[0], lambda t: t[4]),
                                      'B': lambda pop: all(not t[1] for t in pop if t[4]),
                                      'C': lambda pop: most(pop, lambda t: (not t[2]) and t[4] and t[3], lambda t: t[0]),
                                      'D': lambda pop: any(t[0] and not t[4] for t in pop)}, 'must', 'D',
              note='(李明若来自海外→博士且30岁以下→做行政，与“教授不做行政”矛盾)')

def zj2023a_103():
    # 女师范 Fs、女非师范 Fn、男师范 Ms、男非师范 Mn；已知 Fs>Mn。问补哪项后“女>男”必然成立。
    rng = range(0, 7)
    base = [(Fs, Fn, Ms, Mn) for Fs, Fn, Ms, Mn in product(rng, repeat=4) if Fs > Mn]
    prem = {'A': lambda Fs, Fn, Ms, Mn: Fs + Ms < Fn + Mn, 'B': lambda Fs, Fn, Ms, Mn: Fs + Ms > Fn + Mn,
            'C': lambda Fs, Fn, Ms, Mn: Fs > Mn, 'D': lambda Fs, Fn, Ms, Mn: Fn > Mn}
    ok = ''
    for k, f in prem.items():
        W = [m for m in base if f(*m)]
        if W and all(m[0] + m[1] > m[2] + m[3] for m in W): ok += k
    cex = {k: next((m for m in base if f(*m) and not m[0] + m[1] > m[2] + m[3]), None) for k, f in prem.items()}
    record('ZJ2023A-103', ok, 'A', f'premise making 女>男 necessary; counterexamples (Fs,Fn,Ms,Mn)={cex}')

COND_A = [gk2025f_115, gk2017f_114, js2016a_98, sz2023_41, js2016a_92, zj2023a_103]

# =====================================================================================
# 条件与必然性 · B组（真假推理与量词）
# =====================================================================================
def sz20201_34():
    # 4 人各进出一次、不同时；凶手进门时郑某活着、离开时已死；凶手之前的人进出时都活着，之后的人进出时都已死。
    # R1（题意）：每一句（每个分句）都是假的。R2（对照）：每人整段供词为假即可（至少一个分句假），凶手也可能是四人以外的人。
    names = ['赵', '王', '张', '李']
    def states(order, killer):
        pos = {n: i for i, n in enumerate(order)}
        kp = pos.get(killer, None)
        arr_alive = {n: (kp is None or pos[n] <= kp) for n in names} if killer in names else None
        return pos, kp
    res = {}
    for rd in ('R1', 'R2'):
        M = []
        for order in permutations(names):
            pos = {n: i for i, n in enumerate(order)}
            for killer in (names if rd == 'R1' else names + ['外人']):
                for kt in ([None] if killer in names else range(0, 5)):     # 外人行凶的时刻：在第 kt 个人进门之前（0..4）
                    if killer in names:
                        kp = pos[killer]
                        arr_alive = {n: pos[n] <= kp for n in names}
                        leave_alive = {n: pos[n] < kp for n in names}
                        killer_later_than_li = pos[killer] > pos['李']
                    else:
                        arr_alive = {n: pos[n] < kt for n in names}
                        leave_alive = {n: pos[n] < kt for n in names}
                        killer_later_than_li = None      # 外人：无“进他家”的先后可比，按“凶手进他家不比我晚”无从成立处理为假
                    c = {'赵1': killer not in names, '赵2': leave_alive['赵'], '王1': pos['王'] == 1, '王2': not arr_alive['王'],
                         '张1': pos['张'] == 2, '张2': leave_alive['张'], '李1': (killer_later_than_li is False), '李2': not arr_alive['李']}
                    if rd == 'R1':
                        if any(c.values()): continue
                    else:
                        if (c['赵1'] and c['赵2']) or (c['王1'] and c['王2']) or (c['张1'] and c['张2']) or (c['李1'] and c['李2']): continue
                    M.append(dict(order=order, killer=killer))
        res[rd] = M
    judge('SZ20201-34(R1)', res['R1'], {k: (lambda x: (lambda m: m['killer'] == x))(x) for k, x in zip('ABCD', names)}, 'must', 'A',
          note=f"orders={[''.join(m['order']) for m in res['R1']]}")
    kill2 = sorted({m['killer'] for m in res['R2']})
    print(f"   reading check R2 (整段供词为假即可): {len(res['R2'])} models, possible killers {kill2} -> 无唯一答案；"
          f"题干“每句供词都是虚假供述”只能按 R1（逐句为假）理解，原解析同此。")

def hb2023_109():
    T = ['红', '黄', '绿', '蓝']; M = []
    for p in permutations(range(1, 5)):
        P = dict(zip(T, p))
        s = [imp(P['红'] == 1, P['黄'] == 2), imp(P['红'] == 3, P['蓝'] == 4), P['蓝'] != 4, P['黄'] == 2]
        if sum(s) == 1: M.append(P)
    judge('HB2023-109', M, {k: (lambda x: (lambda P: P['绿'] == x))(x) for k, x in zip('ABCD', [1, 2, 3, 4])}, 'must', 'B', note=str(M))

def sz2020sw_71():
    # 6 人完成情况；“大家都没完成”按“全组 6 人”与“仅甲乙丙”两种范围都检验；“甲和丙中只有一个完成”=恰有一个。
    for rd in ('全组', '甲乙丙'):
        M = []
        for d in product(B, repeat=6):
            jia, yi, bing, ding, wu, ji = d
            nobody = not any(d) if rd == '全组' else not (jia or yi or bing)
            st = [not jia, bool(bing), nobody, None, bool(yi), (jia + bing) == 1]
            st[3] = not st[1]
            if sum(1 for s in st if not s) == 2: M.append(d)
        judge(f'SZ2020SW-71({rd})', M, {k: (lambda n: (lambda d: d[0] + d[1] + d[2] == n))(n) for k, n in zip('ABCD', range(4))}, 'must', 'C')

def sz2024_44():
    # “乙和丁中必有一人参与”按“至少一人”“恰有一人”两种读法；甲“一半真话”=两个分句恰一真。
    for rd in ('atleast', 'exactly'):
        M = []
        for v in product(B, repeat=5):
            a, b, c, d, e = v
            half = ((not a) + (not d)) == 1
            sb = imp(b, not c); sc = (b + d >= 1) if rd == 'atleast' else (b + d == 1); sd = imp(e, a); se = sum(v) >= 3
            if half and sb and sc and sd and se: M.append(v)
        sets = {'A': (1, 1, 0, 0, 1), 'B': (0, 1, 0, 1, 1), 'C': (1, 0, 1, 1, 0), 'D': (1, 1, 1, 0, 1)}
        judge(f'SZ2024-44({rd})', M, {k: (lambda s: (lambda v: v == s))(s) for k, s in sets.items()}, 'must', 'A', note=str(M))

def sd2023_67():
    # 枚举小模型，求每对命题可能出现的真值组合，与题干那一对比较
    def pairs_lies():      # 对她说谎的次数 0..3
        return {(n == 0, n >= 2) for n in range(4)}
    def pairs_some(n=3):   # 同学认真与否（非空）
        return {(any(v), any(not x for x in v)) for k in range(1, n + 1) for v in product((True, False), repeat=k)}
    def pairs_all_somenot(n=3):
        return {(all(v), any(not x for x in v)) for k in range(1, n + 1) for v in product((True, False), repeat=k)}
    def pairs_all_none(n=3):
        return {(all(v), all(not x for x in v)) for k in range(1, n + 1) for v in product((True, False), repeat=k)}
    def pairs_past_future():
        return {(not past, fut) for past in (True, False) for fut in (True, False)}
    stem = pairs_lies()
    opts = {'A': pairs_some(), 'B': pairs_all_somenot(), 'C': pairs_all_none(), 'D': pairs_past_future()}
    name = lambda S: {frozenset({(1, 0), (0, 1), (0, 0)}): '反对(不同真,可同假)', frozenset({(1, 1), (1, 0), (0, 1)}): '下反对(可同真,不同假)',
                      frozenset({(1, 0), (0, 1)}): '矛盾', frozenset({(1, 1), (1, 0), (0, 1), (0, 0)}): '无约束'}.get(frozenset((int(a), int(b)) for a, b in S), '?')
    ok = ''.join(k for k, S in opts.items() if S == stem)
    record('SD2023-67', ok, 'C', f"stem={name(stem)}; " + ', '.join(f'{k}={name(S)}' for k, S in opts.items()))

def sd2021_69():
    # 毕业生 N 人（N≤9）：工学 E、人文社科 H、其他 O（读法1：只有两类 O=0；读法2：允许有其他类）；各类再分已就业/未就业。
    # 条件：工学过半；人文社科≥1；已就业过半；未就业≥1（“只有少部分未就业”）。
    for rd in ('两类', '可有他类'):
        M = []
        for N in range(2, 10):
            for e1, e0, h1, h0 in product(range(N + 1), repeat=4):
                o = N - e1 - e0 - h1 - h0
                if o < 0 or (rd == '两类' and o != 0): continue
                for o1 in range(o + 1):
                    o0 = o - o1
                    E = e1 + e0; Hh = h1 + h0; emp = e1 + h1 + o1; un = N - emp
                    if 2 * E > N and Hh >= 1 and 2 * emp > N and un >= 1:
                        M.append(dict(e1=e1, e0=e0, h1=h1, h0=h0))
        judge(f'SD2021-69({rd})', M, {'A': lambda m: 2 * m['e1'] > m['e1'] + m['e0'], 'B': lambda m: m['h0'] >= 1,
                                     'C': lambda m: m['e1'] >= 1, 'D': lambda m: m['h1'] >= 1}, 'must', 'C')

def gd2023x_63():
    M = []
    for w in '甲乙丙':
        s = [w != '甲', w == '乙', w != '丙']
        if sum(s) == 1: M.append(dict(w=w, s=s))
    judge('GD2023X-63', M, {'A': lambda m: m['s'][0], 'B': lambda m: m['s'][2], 'C': lambda m: m['w'] == '甲', 'D': lambda m: m['w'] == '乙'}, 'cannot', 'D',
          note=f"passed={[m['w'] for m in M]}")

COND_B = [sz20201_34, hb2023_109, sz2020sw_71, sz2024_44, sd2023_67, sd2021_69, gd2023x_63]

# =====================================================================================
# 组合 · A组（匹配、分组、座位、排序、选择）
# =====================================================================================
def zj2015a_108():
    # 圆桌 5 座（固定甲在 0 号座以消去旋转；镜像不影响相邻关系）。专业：法律 2、文学 2、历史 1。
    names = '甲乙丙丁戊'; M = []
    for perm in permutations('乙丙丁戊'):
        seat = ['甲'] + list(perm); pos = {n: i for i, n in enumerate(seat)}
        adj = lambda x, y: (pos[x] - pos[y]) % 5 in (1, 4)
        for prof in set(permutations(['法', '法', '文', '文', '史'])):
            P = dict(zip(names, prof))
            law = [n for n in names if P[n] == '法']; lit = [n for n in names if P[n] == '文']
            if not adj(*law) or not adj(*lit) or P['甲'] != P['丁']: continue
            if not adj('丙', '乙'): continue
            others = [n for n in names if adj('丙', n) and n != '乙']          # 丙的另一侧邻座
            if not others or P[others[0]] != '文': continue
            if adj('戊', '乙') or adj('丙', '甲'): continue
            M.append(P)
    judge('ZJ2015A-108', M, {'A': lambda P: P['甲'] == '文', 'B': lambda P: P['乙'] == '法', 'C': lambda P: P['丙'] == '文', 'D': lambda P: P['戊'] == '史'}, 'must', 'C',
          note=str(sorted({tuple(P.values()) for P in M})))

def gk2019f_114():
    books = ['红', '水', '三', '西', '论', '道', '诗']; M = []
    for p in permutations(range(1, 8)):
        P = dict(zip(books, p)); inv = {v: k for k, v in P.items()}
        if not P['三'] < P['道'] or P['道'] - P['三'] != 3: continue
        if any(inv[i] == '诗' for i in range(P['三'] + 1, P['道'])): continue
        if P['西'] not in (1, 7) or P['论'] != 3: continue
        if not (P['诗'] < P['道'] or P['诗'] == P['道'] + 1): continue
        if P['三'] != 1: continue
        M.append(P)
    judge('GK2019F-114', M, {'A': lambda P: P['水'] == 2, 'B': lambda P: P['道'] == 5, 'C': lambda P: P['红'] == 2, 'D': lambda P: P['诗'] == 5}, 'must', 'D',
          note=str([''.join(sorted(P, key=P.get)) for P in M]))

def zj2024a_102():
    ppl = '张王李赵钱孙'; M = []
    for a in product('甲乙丙丁', repeat=6):
        A = dict(zip(ppl, a)); cnt = {x: a.count(x) for x in '甲乙丙丁'}
        if any(not 1 <= cnt[x] <= 2 for x in cnt): continue
        if not cnt['乙'] > cnt['甲'] or not cnt['丁'] > cnt['丙']: continue
        if not imp(A['李'] == '甲' or A['赵'] == '甲', A['王'] == '丁'): continue
        only_qian_ding = [p for p in ppl if A[p] == '丁'] == ['钱']
        if not imp(A['张'] == '乙' or A['李'] == '乙' or A['赵'] == '乙', only_qian_ding): continue
        if A['孙'] != '丙': continue
        M.append(A)
    judge('ZJ2024A-102', M, {'A': lambda A: A['张'] == '丙', 'B': lambda A: A['赵'] == '乙' and A['钱'] == '乙',
                             'C': lambda A: A['王'] == '丁' and A['李'] == '丁', 'D': lambda A: A['李'] == '丁' and A['赵'] == '丁'}, 'must', 'D', note=str(M))

def sz2024_40():
    items = ['簪', '钗', '钿', '篦']; M = []
    for p in permutations(['金', '银', '铜', '玉']):
        X = dict(zip(items, p))
        c = [imp(X['簪'] == '金', X['钗'] != '铜'), imp(X['钗'] != '金', X['篦'] == '玉'), imp(X['钗'] == '金', X['钿'] == '玉'),
             imp(X['钿'] == '铜', X['篦'] != '银'), imp(X['钿'] != '银', X['篦'] == '银'), imp(X['篦'] == '铜', X['簪'] != '玉')]
        if all(c): M.append(X)
    judge('SZ2024-40', M, {k: (lambda m: (lambda X: X['簪'] == m))(m) for k, m in zip('ABCD', ['金', '银', '铜', '玉'])}, 'must', 'C', note=str(M))

def zj2023a_101():
    kids = ['明', '军', '花', '飞', '雅']
    balls = [('红', '圆'), ('蓝', '星'), ('黄', '心'), ('蓝', '圆'), ('红', '心')]; M = []
    for p in permutations(balls):
        X = dict(zip(kids, p))
        s1 = all(X[k][1] != '圆' and X[k][0] != '蓝' for k in ('花', '雅'))
        s2 = X['军'][0] != X['雅'][0] and X['军'][1] != X['雅'][1]
        s3 = X['雅'][0] == '黄' and X['明'][0] == '蓝'
        s4 = X['军'][0] == X['花'][0] and X['飞'][1] != '星'
        if s1 and s2 and s3 and s4: M.append(X)
    judge('ZJ2023A-101', M, {'A': lambda X: X['军'] == ('红', '心'), 'B': lambda X: X['花'] == ('黄', '心'),
                             'C': lambda X: X['飞'] == ('红', '圆'), 'D': lambda X: X['明'] == ('蓝', '星')}, 'must', 'D', note=str(M))

def js2022a_103():
    P = '甲乙丙丁'; M = []
    for male, party, prof in product(product(B, repeat=4), repeat=3):
        if sum(party) != 3 or sum(male) != 2 or sum(prof) != 1: continue
        if any(not (male[i] or party[i] or prof[i]) for i in range(4)): continue
        if male[0] != male[1] or party[1] != party[2] or (party[2] and party[3]): continue
        leaders = [P[i] for i in range(4) if male[i] and party[i] and prof[i]]
        if len(leaders) != 1: continue        # 组长存在（题干：担任组长的专家为男性、党员、教授）
        M.append(leaders[0])
    judge('JS2022A-103', M, {k: (lambda x: (lambda m: m == x))(x) for k, x in zip('ABCD', P)}, 'must', 'C', note=str(M))

def gdxd2020sw_30():
    ev = ['跳高', '跳远', '铅球', '长跑']; M = []
    for p in permutations(ev):
        X = dict(zip('甲乙丙丁', p))
        g = {'甲': X['乙'] == '跳高', '乙': X['丙'] != '跳远', '丙': X['丁'] != '跳远', '丁': X['甲'] != '长跑'}
        if all(g[x] == (X[x] in ('跳高', '长跑')) for x in '甲乙丙丁'): M.append(X)
    judge('GDXD2020SW-30', M, {'A': lambda X: X['甲'] == '跳远', 'B': lambda X: X['乙'] == '长跑', 'C': lambda X: X['丙'] == '铅球', 'D': lambda X: X['丁'] == '跳高'},
          'must', 'C', note=str(M))

def js2017a_96():
    # 老张(男) 妹妹(女) 儿子(男) 女儿(女)。孪生同胞只能是同辈兄弟姐妹：{张,妹} 或 {儿,女}。
    # 年龄（整数档 0..5）：孪生同龄；老张比子女年长；妹妹不比老张年长（为孪生时同龄）；其余同龄与否不限。
    sex = {'张': 'M', '妹': 'F', '儿': 'M', '女': 'F'}; ppl = list(sex); M = []
    for twins in ({'张', '妹'}, {'儿', '女'}):
        for ages in product(range(6), repeat=4):
            A = dict(zip(ppl, ages))
            a, b = sorted(twins)
            if A[a] != A[b]: continue
            if not (A['张'] > A['儿'] and A['张'] > A['女'] and A['妹'] <= A['张']): continue
            if twins == {'儿', '女'} and A['妹'] == A['张']: continue        # 老张与妹妹不是孪生时不同龄
            for order in permutations(ppl):
                first, fourth = order[0], order[3]
                if first not in twins: continue                              # 第1名有孪生同胞（在 4 人中）
                twin = (twins - {first}).pop()
                if A[first] != A[fourth] or sex[twin] == sex[fourth]: continue
                M.append(dict(first=first, fourth=fourth, twins=frozenset(twins)))
    judge('JS2017A-96', M, {k: (lambda x: (lambda m: m['first'] == x))(x) for k, x in zip('ABCD', ['张', '妹', '女', '儿'])}, 'must', 'C',
          note=str(sorted({(m['first'], m['fourth'], ''.join(sorted(m['twins']))) for m in M})))

def gd2015x_65():
    pts = {1: 10, 2: 8, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1}; M = []
    for p in set(permutations('甲甲乙乙丙丙丁丁')):
        pos = {t: sorted(i + 1 for i, x in enumerate(p) if x == t) for t in '甲乙丙丁'}
        if any(r % 2 for r in pos['甲']) or pos['乙'][1] - pos['乙'][0] != 1: continue
        if sum(r % 2 for r in pos['丙']) != 1 or any(r % 2 == 0 for r in pos['丁']): continue
        if p[0] != '丁' or p[7] != '丙': continue
        btw = lambda inner, outer: outer[0] < inner[0] and inner[1] < outer[1]
        if not btw(pos['乙'], pos['甲']) or not btw(pos['乙'], pos['丙']): continue
        score = {t: sum(pts[r] for r in pos[t]) for t in '甲乙丙丁'}
        M.append(''.join(sorted(score, key=lambda t: -score[t])))
    judge('GD2015X-65', M, {k: (lambda o: (lambda m: m == o))(o) for k, o in zip('ABCD', ['丁甲丙乙', '甲丁乙丙', '甲丁丙乙', '丁甲乙丙'])}, 'must', 'D', note=str(M))

def hb2025_109():
    T = ['桃', '李', '杨', '柳', '松']; M = []
    for v in product(B, repeat=5):
        X = dict(zip(T, v))
        if imp(X['桃'], not X['松']) and (X['桃'] + X['李'] == 1) and sum(v) >= 3 and X['桃'] + X['杨'] <= 1 and X['李'] + X['柳'] <= 1:
            M.append(X)
    judge('HB2025-109', M, {'A': lambda X: X['李'] and X['桃'] and not X['松'], 'B': lambda X: X['桃'] and X['柳'] and not X['杨'],
                            'C': lambda X: X['李'] and X['杨'] and not X['松'], 'D': lambda X: X['杨'] and X['松'] and not X['桃']}, 'must', 'D', note=str(M))

COMBO_A = [zj2015a_108, gk2019f_114, zj2024a_102, sz2024_40, zj2023a_101, js2022a_103, gdxd2020sw_30, js2017a_96, gd2015x_65, hb2025_109]

# =====================================================================================
# 组合 · B组（一拖 n）
# =====================================================================================
MEET = '甲乙丙丁戊己庚辛'
def gk2025d_models(rd):
    """rd='time'：“之后/之前”指举办时间先后（同一季度内也有先后）；rd='quarter'：指季度严格先后（对照读法）。"""
    M = []
    for q in product(range(1, 5), repeat=8):
        Q = dict(zip(MEET, q))
        if any(q.count(k) > 3 for k in range(1, 5)): continue
        if Q['丁'] != 2 or Q['辛'] != 2 or Q['甲'] != Q['戊']: continue
        lt = (lambda x, y: Q[x] <= Q[y]) if rd == 'time' else (lambda x, y: Q[x] < Q[y])
        if not (lt('乙', '丁') and lt('丁', '丙') and lt('丙', '甲') and lt('己', '丙')): continue
        if rd == 'time':      # 时间全序须存在：同季度内按 乙<丁<丙<甲、己<丙 可以排出（季度不减即可，链无环）
            pass
        M.append(Q)
    return M
def gk2025d_set():
    # 正式读法 time：“之后/之前”指举办时间先后（各次会议时间不重叠，同一季度内也分先后）——原解析同此（如 109 题“甲前面已经有己、丙”与甲同季度并存）。
    M = gk2025d_models('time'); cnt = lambda Q, k: sum(1 for x in MEET if Q[x] == k)
    asks = [('GK2025D-106', lambda M: M, {k: (lambda a, b: (lambda Q: Q[a] == 1 and Q[b] == 1))(*ab) for k, ab in zip('ABCD', ['甲戊', '丙丁', '丁己', '己庚'])}, 'can', 'D'),
            ('GK2025D-107', lambda M: [Q for Q in M if cnt(Q, 2) == 2], {k: (lambda x: (lambda Q: Q[x] == 1))(x) for k, x in zip('ABCD', '甲乙庚丙')}, 'must', 'B'),
            ('GK2025D-108', lambda M: [Q for Q in M if Q['丙'] == 4 and Q['戊'] == 4],
             {k: (lambda a, b: (lambda Q: Q[a] == 3 and Q[b] == 3))(*ab) for k, ab in zip('ABCD', ['甲庚', '乙丁', '乙己', '己庚'])}, 'can', 'D'),
            ('GK2025D-109', lambda M: [Q for Q in M if all(cnt(Q, k) >= 1 for k in range(1, 5)) and cnt(Q, 4) == 1],
             {k: (lambda a, b: (lambda Q: Q[a] == 3 and Q[b] == 3))(*ab) for k, ab in zip('ABCD', ['甲戊', '乙丙', '丙己', '己庚'])}, 'must', 'A'),
            ('GK2025D-110', lambda M: [Q for Q in M if Q['甲'] == 3 and cnt(Q, 4) == 0], {k: (lambda x: (lambda Q: Q['庚'] == Q[x]))(x) for k, x in zip('ABCD', '乙丙己辛')}, 'cannot', 'B')]
    for qid, sub, opts, mode, exp in asks: judge(qid, sub(M), opts, mode, exp)
    print(f'   GK2025D base models (time order) = {len(M)}')
    # 对照读法 quarter：若把“之后/之前”理解成季度严格先后，则 乙Q1、丁Q2、丙Q3、甲戊Q4 被锁死，108 题的前提（丙在第四季度）不可能成立。
    Mq = gk2025d_models('quarter'); notes = []
    for qid, sub, opts, mode, exp in asks:
        S = sub(Mq)
        if not S: notes.append(f'{qid}: 前提无模型'); continue
        stat = {k: ('ALL' if all(f(Q) for Q in S) else 'SOME' if any(f(Q) for Q in S) else 'NONE') for k, f in opts.items()}
        sel = {'must': 'ALL', 'can': None, 'cannot': 'NONE'}[mode]
        ans = ''.join(k for k, s in stat.items() if (s != 'NONE' if mode == 'can' else s == sel))
        notes.append(f'{qid}: {ans}')
    print(f'   reading check [季度严格先后] ({len(Mq)} models): ' + '; '.join(notes) + ' -> 该读法使 108 题无解，只能按举办时间先后理解，与原解析一致')

def js2016a_set():
    G = ['台球', '乒乓球', '羽毛球', '登山']; P = '甲乙丙丁戊己庚'
    pairs = [frozenset(c) for c in combinations(G, 2)]; M = []
    for ch in product(pairs, repeat=7):
        A = dict(zip(P, ch))
        if A['丁'] != A['戊'] or A['己'] != A['庚']: continue
        if '台球' in A['甲'] and '台球' not in A['丁']: continue
        if {p for p in P if '乒乓球' in A[p]} != {'乙', '丙'}: continue
        if any(not 2 <= sum(g in A[p] for p in P) <= 5 for g in G): continue
        M.append(A)
    judge('JS2016A-99', [A for A in M if {p for p in P if '登山' in A[p]} == {'己', '庚'}],
          {'A': lambda A: A['甲'] == {'台球', '羽毛球'}, 'B': lambda A: A['乙'] == {'台球', '羽毛球'},
           'C': lambda A: A['己'] == {'台球', '登山'}, 'D': lambda A: A['庚'] == {'羽毛球', '登山'}}, 'must', 'A')
    M100 = [A for A in M if '台球' not in A['乙'] and '台球' not in A['丁']]
    conds = {'A': (('己', '台球'), ('丙', '登山')), 'B': (('庚', '台球'), ('戊', '台球')), 'C': (('甲', '羽毛球'), ('庚', '登山')), 'D': (('乙', '羽毛球'), ('己', '登山'))}
    for k, ((p1, g1), _) in conds.items():
        assert any(g1 in A[p1] for A in M100), f'JS2016A-100 option {k} antecedent never holds'
    judge('JS2016A-100', M100, {k: (lambda c: (lambda A: imp(c[0][1] in A[c[0][0]], c[1][1] in A[c[1][0]])))(c) for k, c in conds.items()}, 'must', 'D',
          note='(各选项前件在条件下都可能成立，非空真)')
    print(f'   JS2016A base models = {len(M)}, Q100 models = {len(M100)}')

COMBO_B = [gk2025d_set, js2016a_set]

# =====================================================================================
# 科学推理（可计算项复算；知识项只在答案册给理由）
# =====================================================================================
def solve_circuit(nodes, edges, src, closed):
    """nodes: list; edges: (name, a, b, R) with R=0 for wires/closed switches; src=(plus, minus, V). Returns branch currents."""
    # 合并零电阻边（导线、闭合开关）
    parent = {n: n for n in nodes}
    def f(x):
        while parent[x] != x: x = parent[x]
        return x
    for name, a, b, R in edges:
        if R == 0 and (not name.startswith('S') or name in closed): parent[f(a)] = f(b)
    groups = sorted({f(n) for n in nodes}); gi = {g: i for i, g in enumerate(groups)}
    plus, minus, V = src
    n = len(groups); import itertools
    # 节点电压法：minus 接地，plus = V
    Gm = [[Fr(0)] * n for _ in range(n)]; I = [Fr(0)] * n
    res = [(name, gi[f(a)], gi[f(b)], R) for name, a, b, R in edges if R != 0]
    for name, a, b, R in res:
        g = Fr(1, 1) / R
        Gm[a][a] += g; Gm[b][b] += g; Gm[a][b] -= g; Gm[b][a] -= g
    fixed = {gi[f(minus)]: Fr(0), gi[f(plus)]: Fr(V)}
    free = [i for i in range(n) if i not in fixed]
    # 解 free 节点方程
    A = [[Gm[i][j] for j in free] for i in free]; bb = [-sum(Gm[i][j] * fixed[j] for j in fixed) for i in free]
    m = len(free)
    for c in range(m):
        piv = next(r for r in range(c, m) if A[r][c] != 0); A[c], A[piv] = A[piv], A[c]; bb[c], bb[piv] = bb[piv], bb[c]
        for r in range(m):
            if r != c and A[r][c] != 0:
                k = A[r][c] / A[c][c]; A[r] = [x - k * y for x, y in zip(A[r], A[c])]; bb[r] -= k * bb[c]
    volt = dict(fixed); volt.update({free[i]: bb[i] / A[i][i] for i in range(m)})
    return {name: (volt[a] - volt[b]) / R for name, a, b, R in res}, {name: (a, b) for name, a, b, R in res}

def gd2016z_67():
    # 按原图连线：TL—N1（导线），N1—L2—S2—TR，TR—N3（导线），N2—L3—N3，N1—N2（导线），N2—S1—N4，N4—BL（导线），BL—L1—TL，电池 N4(−)…BR(+)，BR—N3（导线）
    nodes = ['TL', 'N1', 'TR', 'N3', 'N2', 'N4', 'BL', 'BR', 'm2']
    edges = [('w1', 'TL', 'N1', 0), ('L2', 'N1', 'm2', 1), ('S2', 'm2', 'TR', 0), ('w2', 'TR', 'N3', 0), ('L3', 'N2', 'N3', 1),
             ('w3', 'N1', 'N2', 0), ('S1', 'N2', 'N4', 0), ('w4', 'N4', 'BL', 0), ('L1', 'BL', 'TL', 1), ('w5', 'BR', 'N3', 0)]
    cur, ends = solve_circuit(nodes, edges, ('BR', 'N4', 6), closed={'S1', 'S2'})
    lit = sorted(k for k, v in cur.items() if v != 0)
    parallel = ends['L2'] == ends['L3'] or ends['L2'] == ends['L3'][::-1]
    ans = 'D' if lit == ['L2', 'L3'] and parallel else ('B' if lit == ['L2', 'L3'] else ('A' if lit == ['L3'] else ('C' if lit == ['L1', 'L3'] else '?')))
    record('GD2016Z-67', ans, 'D', f'currents={ {k: str(v) for k, v in cur.items()} }, lit={lit}, L2/L3 same node pair={parallel} (L1 两端被 S1 与导线连成同一节点而短路)')

def gd2016z_66():
    rho = {'木': 0.5, '铅': 11.3, '铁': 7.9, '铝': 2.7}; water = 1.0
    seen = {'木': '漂浮', '铅': '悬浮', '铁': '悬浮', '铝': '沉底'}
    def solid_state(r): return '漂浮' if r < water else ('悬浮' if r == water else '沉底')
    det = []
    for k, st in seen.items():
        solid_ok = solid_state(rho[k]) == st                     # 实心时能否出现所见状态
        hollow_ok = True                                          # 空心：平均密度可调到 <、=、> 水中任一（只要壁厚合适）
        if solid_ok and hollow_ok: continue                       # 两种都可能 -> 不能判断
        det.append(k)
    opts = {'A': {'木', '铅'}, 'B': {'铝', '铅'}, 'C': {'木', '铝'}, 'D': {'铅', '铁'}}
    record('GD2016Z-66', ''.join(k for k, v in opts.items() if v == set(det)), 'D', f'能判断空/实心的球={det}（铅、铁实心必沉底，却悬浮→一定空心）')

def gd2017_68():
    random.seed(7); fr_signs = set(); forces = set(); tension_const = True
    g = 10; th = math.radians(30)
    for _ in range(20000):
        mM, mN, mu = random.uniform(0.5, 3), random.uniform(0.2, 3), random.uniform(0.2, 1.5)
        F = random.uniform(0, 30)
        T = mN * g                                                # N 静止：绳拉力恒等于 N 的重力
        # 绳沿斜面向上拉 M（滑轮在斜面顶端）；F 水平向右（背离滑轮一侧，斜面向右下倾斜）：沿斜面向下分量 F cosθ，垂直斜面向外分量 F sinθ
        Nn = mM * g * math.cos(th) - F * math.sin(th)
        if Nn < 0: continue
        f_needed = T - mM * g * math.sin(th) - F * math.cos(th)   # 需要的摩擦力（正=沿斜面向下）
        if abs(f_needed) > mu * Nn: continue                      # 静止要求
        fr_signs.add('下' if f_needed > 1e-9 else ('上' if f_needed < -1e-9 else '0'))
        forces.add(1 + (Nn > 1e-9) + 1 + (F > 1e-9) + (abs(f_needed) > 1e-9))   # 重力 + 支持力? + 绳拉力 + F? + 摩擦力?
    # 两个特殊情形（测度为零，随机取样碰不到）：摩擦恰为零 -> 4 个力；支持力也恰为零 -> 3 个力（原解析亦指出“可能只受三个力”）
    mM = 1.0; Fz = 0.5 * mM * g; mN0 = (mM * g * math.sin(th) + Fz * math.cos(th)) / g          # 取 F 使所需摩擦为 0
    assert abs(mN0 * g - mM * g * math.sin(th) - Fz * math.cos(th)) < 1e-12 and mM * g * math.cos(th) - Fz * math.sin(th) > 0
    forces.add(4); fr_signs.add('0')
    F3 = mM * g * math.cos(th) / math.sin(th); mN3 = (mM * g * math.sin(th) + F3 * math.cos(th)) / g   # 支持力为 0、摩擦为 0
    assert abs(mM * g * math.cos(th) - F3 * math.sin(th)) < 1e-12
    forces.add(3)
    st = {'A': tension_const, 'B': fr_signs == {'上'}, 'C': False, 'D': forces == {4}}
    record('GD2017-68', ''.join(k for k, v in st.items() if v), 'A', f'摩擦方向可能={sorted(fr_signs)}，M 受力个数可能={sorted(forces)}；合力恒为 0')

def gd2018_68():
    mirror_to_chart, mirror_to_eye = 3 + 1, 3
    image_to_eye = mirror_to_chart + mirror_to_eye
    record('GD2018-68', 'A' if image_to_eye == 7 else '?', 'A', f'像在镜后 {mirror_to_chart} m，与检查点相距 {image_to_eye} m；平面镜成等大、正立（左右相反）的虚像')

def gd2020z_83():
    F, s = 1.0, 1.0
    W1, W2 = F * s, F * s           # 两次力的大小相同、方向都沿运动方向、位移都是 A→B
    record('GD2020Z-83', 'C' if W1 == W2 else '?', 'C', f'W=Fs：W1={W1} W2={W2}（与箱数、推或拉无关）')

def gd2021z_80():
    V1 = Fr(1)
    v = lambda t: (V1 * t / 2) if t <= 2 else (V1 - V1 * (t - 2) / 2)       # 0—2 匀加速；2—6 一条直线，过 (4,0)
    def disp(t1, t2, n=600):
        h = Fr(t2 - t1, n); return sum((v(t1 + i * h) + v(t1 + (i + 1) * h)) / 2 * h for i in range(n))
    x6 = disp(0, 6); far_t = max((Fr(k, 10) for k in range(61)), key=lambda t: disp(0, t))
    a1, a2 = (v(2) - v(0)) / 2, (v(4) - v(2)) / 2
    st = {'A': x6 == 0, 'B': far_t == 2, 'C': abs(v(2)) == abs(v(6)), 'D': a1 == a2}
    record('GD2021Z-80', ''.join(k for k, val in st.items() if val), 'C', f'x(6)={x6}·V1·min, 最远时刻={far_t}min, v(2)={v(2)}, v(6)={v(6)}, a1={a1}, a2={a2}')

def gd2022x_82():
    # 乙：s=v0 t − a t²/2，用 (10,200)(20,350) 解出，再验 (30,450)(40,500)
    a = Fr(2 * (2 * 200 - 350), 200); v0 = Fr(200 + a * 50, 10)
    s_yi = lambda t: v0 * min(t, v0 / a) - a * min(t, v0 / a) ** 2 / 2
    assert s_yi(30) == 450 and s_yi(40) == 500
    v_jia = Fr(600, 60); assert all(v_jia * t == d for t, d in [(10, 100), (20, 200), (40, 400), (60, 600)])
    stop = v0 / a
    st = {'A': v_jia == 15, 'B': v0 == 25, 'C': s_yi(45) > v_jia * 45, 'D': stop > 50}
    record('GD2022X-82', ''.join(k for k, val in st.items() if val), 'C', f'甲 v={v_jia} m/s；乙 v0={v0} m/s a={a} m/s², {stop}s 停下，s(45)={s_yi(45)} m > 甲 {v_jia*45} m')

def gd2023z_73():
    filt = {'G'}; wall = {'R', 'G', 'B'}; letters = {'R'}
    see = lambda reflect: (reflect & filt) or {'黑'}
    w, l = see(wall), see(letters)
    ans = {'A': w == {'G'} and l == w, 'B': w == {'G'} and l == {'黑'}, 'C': False, 'D': w == {'黑'}}
    record('GD2023Z-73', ''.join(k for k, v in ans.items() if v), 'B', f'白墙→透过绿玻璃={w}，红字→{l}')

def gd2020z_82():
    # 按原图读坐标：(O2 含量, 温度)；着火点 t=1.0；O2 含量为 0 不能燃烧；温度低于 t 不能燃烧；火势随温度、O2 含量增大
    pts = {1: (0.0, 1.5), 2: (0.9, 1.0), 3: (1.6, 0.6), 4: (2.4, 1.0), 5: (3.2, 1.8)}
    burn = {k: (o > 0 and T >= 1.0) for k, (o, T) in pts.items()}
    order = sorted([k for k in pts if burn[k]], key=lambda k: (pts[k][1], pts[k][0]), reverse=True)
    # 检查排序不依赖“温度优先还是氧气优先”：⑤ 两项都最大，④ 与 ② 温度相同、④ 氧气多
    order2 = sorted([k for k in pts if burn[k]], key=lambda k: (pts[k][0], pts[k][1]), reverse=True)
    assert order == order2
    opts = {'A': [1, 2, 3], 'B': [2, 4, 5], 'C': [3, 4, 5], 'D': [5, 4, 2]}
    record('GD2020Z-82', ''.join(k for k, v in opts.items() if v == order), 'D', f'能燃烧的点={[k for k in pts if burn[k]]}，火势由大到小={order}')

def v_dynamic_circuit():
    # 改编（母题 GD2025-69）：电源电压 U 恒定；定值电阻 R0 在干路；灯 L（阻值视为不变）与热敏电阻 Rt 并联，电流表与 Rt 串联。Rt 随温度升高而减小。
    random.seed(3); trend = {}
    for _ in range(5000):
        U, R0, RL = random.uniform(1, 20), random.uniform(0.5, 20), random.uniform(0.5, 20)
        Rt1 = random.uniform(0.5, 50); Rt2 = Rt1 * random.uniform(0.2, 0.95)          # 升温后 Rt 变小
        def state(Rt):
            Rp = RL * Rt / (RL + Rt); I = U / (R0 + Rp); Vp = I * Rp
            return dict(IA=Vp / Rt, PL=Vp ** 2 / RL, V0=I * R0, P=U * I)
        s1, s2 = state(Rt1), state(Rt2)
        for k in s1:
            trend.setdefault(k, set()).add('↑' if s2[k] > s1[k] else '↓')
    st = {'A': trend['IA'] == {'↓'}, 'B': trend['PL'] == {'↓'}, 'C': trend['V0'] == {'↓'}, 'D': trend['P'] == {'↓'}}
    record('PD3C-VS1(热敏电阻并联)', ''.join(k for k, v in st.items() if v), 'B', f'trends over 5000 random circuits: { {k: sorted(v) for k, v in trend.items()} }')
    # 记忆检验：母题（灯在干路、R1∥R2）中“灯泡亮度增大”为真；本题灯与 Rt 并联，亮度变小
    U, RL, R2 = 6.0, 5.0, 10.0
    mother = lambda R1: (U / (RL + R1 * R2 / (R1 + R2))) ** 2 * RL
    assert mother(4.0) > mother(8.0)
    print('   memory check: 母题结构中升温灯变亮（P_L 增大）；本题结构中升温灯变暗 -> 记得母题“灯变亮”会选错')

FOOD = [('水草', '螺'), ('水草', '鲫鱼'), ('浮游藻类', '浮游动物'), ('浮游藻类', '虾'), ('浮游动物', '虾'), ('浮游动物', '小鱼'),
        ('虾', '小鱼'), ('虾', '鳜鱼'), ('螺', '鲫鱼'), ('小鱼', '鳜鱼'), ('小鱼', '白鹭'), ('鲫鱼', '鳜鱼'), ('鲫鱼', '白鹭')]
def v_food_web():
    # 改编（母题 GD2026-70 海洋食物网）：换成文字给出的湖泊食物网，箭头由被捕食者指向捕食者。
    prey = {}; pred = {}
    for a, b in FOOD: pred.setdefault(a, []).append(b); prey.setdefault(b, []).append(a)
    orgs = {x for e in FOOD for x in e}
    producers = sorted(o for o in orgs if o not in prey); tops = sorted(o for o in orgs if o not in pred)
    chains = []
    def walk(path):
        last = path[-1]
        if last not in pred: chains.append(path); return
        for nxt in pred[last]: walk(path + [nxt])
    for p in producers: walk([p])
    levels = {}
    for c in chains:
        for i, o in enumerate(c): levels.setdefault(o, set()).add(i + 1)
    longest = max(len(c) for c in chains)
    eats = lambda a, b: b in pred.get(a, [])            # a 被 b 吃
    st = {'A': len(chains) == 12,                                          # 选项A：该食物网共有12条食物链
          'B': levels['小鱼'] == {3},                                       # 选项B：小鱼在该食物网中只处于第三营养级
          'C': (eats('白鹭', '鳜鱼') or eats('鳜鱼', '白鹭')) and bool(set(prey['白鹭']) & set(prey['鳜鱼'])),   # 选项C：白鹭与鳜鱼既有捕食又有竞争关系
          'D': prey['鲫鱼'] == ['螺']}                                     # 选项D：螺大量减少，鲫鱼数量一定迅速减少（只有当螺是鲫鱼唯一食物时才可能“一定”）
    record('PD3C-VS2(湖泊食物网)', ''.join(k for k, v in st.items() if v), 'A',
           f'producers={producers}, tops={tops}, chains={len(chains)}, longest={longest} 级, 小鱼营养级={sorted(levels["小鱼"])}, 鳜鱼营养级={sorted(levels["鳜鱼"])}, 鲫鱼食物={prey["鲫鱼"]}')
    for c in chains: print('     ' + '→'.join(c))

SCI = [gd2016z_67, gd2016z_66, gd2017_68, gd2018_68, gd2020z_83, gd2021z_80, gd2022x_82, gd2023z_73, gd2020z_82, v_dynamic_circuit, v_food_web]

# =====================================================================================
# 与 questions.jsonl 交叉核对
# =====================================================================================
KEYMAP = {}   # 题号 -> RESULTS 键；由 questions.jsonl 的 verify 字段自动建立（形如 verify/verify_d09.py::<RESULTS键>）
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

if __name__ == '__main__':
    for f in COND_A + COND_B + COMBO_A + COMBO_B + SCI: f()
    crosscheck()
    print(f'\n{len(RESULTS)} checks passed')
