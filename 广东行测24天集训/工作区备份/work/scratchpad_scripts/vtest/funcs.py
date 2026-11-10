def gk2020f_107():
    # 只翻与“文明”有关的三句：长期自我封闭 fb -> 走向衰落 sl；保持旺盛生命活力 hl -> 交流互鉴 jl ∧ 取长补短 qc（首句“生命有机体”只是类比）
    M = [dict(fb=fb, sl=sl, jl=jl, qc=qc, hl=hl) for fb, sl, jl, qc, hl in product(B, repeat=5) if imp(fb, sl) and imp(hl, jl and qc)]
    judge('GK2020F-107', M, {'A': lambda m: imp(not m['jl'], not m['hl']), 'B': lambda m: imp(not m['fb'], not m['sl']),
                             'C': lambda m: imp(m['jl'] and m['qc'], m['hl']), 'D': lambda m: imp(not m['hl'], not m['qc'])}, 'must', 'A')

def zjxd2020_30():
    # 规则：(甲爱看 ∨ 乙不爱看) -> 丙爱看。问补充哪项能推出“乙爱看”：该项与规则相容，且在所有满足二者的模型中乙都爱看。
    rule = [dict(a=a, b=b, c=c) for a, b, c in product(B, repeat=3) if imp(a or not b, c)]
    prem = {'A': lambda m: not m['c'], 'B': lambda m: not m['a'], 'C': lambda m: m['a'] and m['c'],
            'D': lambda m: (not m['a']) + (not m['c']) == 1,             # “甲和丙有一个不爱看”按“恰有一个”
            'D*': lambda m: (not m['a']) or (not m['c'])}                # 另一读法“至少一个”
    ent = {k: any(f(m) for m in rule) and all(m['b'] for m in rule if f(m)) for k, f in prem.items()}
    assert ent['D'] == ent['D*']
    record('ZJXD2020-30', ''.join(k for k in 'ABCD' if ent[k]), 'A', f'premise entails 乙爱看: {ent}')

def gdxd2019sw_12():
    # 3 家公司：同质化 h、涨价 r、消费者改选其他公司 s；每家 r -> s。“普遍存在同质化”只取多数(>=2家)，不要求全部。
    M = []
    for h in product(B, repeat=3):
        if sum(h) < 2: continue
        for r in product(B, repeat=3):
            for s in product(B, repeat=3):
                if all(imp(r[i], s[i]) for i in range(3)): M.append(dict(h=h, r=r, s=s))
    st = {'Ⅰ': lambda m: all(m['h']),
          'Ⅱ': lambda m: all(imp(not m['r'][i], not m['s'][i]) for i in range(3)),
          'Ⅲ': lambda m: all(imp(not m['s'][i], not m['r'][i]) for i in range(3))}     # 一直选择该家 = 不改选其他公司
    valid = {k for k, f in st.items() if all(f(m) for m in M)}
    opts = {'A': {'Ⅰ'}, 'B': {'Ⅲ'}, 'C': {'Ⅰ', 'Ⅱ'}, 'D': {'Ⅰ', 'Ⅲ'}}
    record('GDXD2019SW-12', ''.join(k for k, v in opts.items() if v == valid), 'B', f'valid statements {sorted(valid)} (models={len(M)})')

def js2017a_97():
    # 死因 ∈ {自杀, 谋杀, 意外}；li = 李某脱不了干系。甲：谋杀 -> li（“正和张某闹离婚”是理由，解析同此译法）；乙：死因不是意外。
    # 赵警官（均为真）：(1) 甲乙同对或同错 -> 意外；(2) 甲乙中有一人错 -> 不是意外。(2) 按“恰有一人错”“至少一人错”两种读法都穷举。
    for rd in ('exactly', 'atleast'):
        M = []
        for cause, li in product(('自杀', '谋杀', '意外'), B):
            j = imp(cause == '谋杀', li); y = cause != '意外'; wrong = (not j) + (not y)
            if imp(j == y, cause == '意外') and imp(wrong == 1 if rd == 'exactly' else wrong >= 1, cause != '意外'):
                M.append(dict(cause=cause, li=li))
        judge(f'JS2017A-97({rd})', M, {'A': lambda m: m['cause'] == '谋杀', 'B': lambda m: m['cause'] == '自杀',
                                       'C': lambda m: m['cause'] == '意外', 'D': lambda m: m['cause'] == '谋杀' and m['li']}, 'must', 'A')
    # 读法说明（不断言）：若把“正和张某闹离婚”也算作甲断言的一部分，死因不再唯一
    for rd in ('exactly', 'atleast'):
        alt = set()
        for cause, li, lh in product(('自杀', '谋杀', '意外'), B, B):
            j = imp(cause == '谋杀', li) and lh; y = cause != '意外'; wrong = (not j) + (not y)
            if imp(j == y, cause == '意外') and imp(wrong == 1 if rd == 'exactly' else wrong >= 1, cause != '意外'): alt.add(cause)
        print(f'   note({rd}): if "正和张某闹离婚" were part of 甲\'s claim, possible causes = {sorted(alt)} -> 按解析译法只判条件句')

def gk2020f_111():
    M = []
    for p in permutations('ABCDF'):
        P = dict(zip('甲乙丙丁戊', p))
        if P['丁'] != 'B': continue
        if not imp(P['甲'] == 'C' or P['乙'] == 'C', P['丙'] == 'B'): continue
        if not imp(P['戊'] == 'C', P['丁'] == 'F'): continue
        M.append(P)
    judge('GK2020F-111', M, {'A': lambda P: P['甲'] == 'A', 'B': lambda P: P['乙'] == 'D', 'C': lambda P: P['丙'] == 'C', 'D': lambda P: P['戊'] == 'F'}, 'must', 'C')

def gk2019f_115():
    # 一周7天、每天2门：周四=民法2门；其余6天两类不同；国际私法在周日；民—行、经—商不同天。穷举周课表，统计各类别能否同天。
    cats = '民经行商国'; need = {'民': 3, '经': 3, '行': 3, '商': 2, '国': 1}          # 周四已用去2门民法
    pairs = [frozenset(x) for x in combinations(cats, 2) if set(x) not in ({'民', '行'}, {'经', '商'})]
    M = []
    for sel in product(pairs, repeat=6):                                             # 周一、二、三、五、六、日
        cnt = dict.fromkeys(cats, 0)
        for pr in sel:
            for c in pr: cnt[c] += 1
        if cnt == need and '国' in sel[5]: M.append(sel)
    tog = lambda S, x, y: frozenset((x, y)) in S
    judge('GK2019F-115', M, {'A': lambda S: tog(S, '经', '国'), 'B': lambda S: tog(S, '行', '经'),
                             'C': lambda S: tog(S, '行', '商'), 'D': lambda S: tog(S, '民', '经')}, 'cannot', 'A')
    never = ['—'.join(p) for p in combinations(cats, 2) if not any(frozenset(p) in S for S in M)]
    print(f'   category pairs never on the same day over {len(M)} weekly schedules: {never}')

def js2019a_93():
    H = '张王李赵'; M = []
    for ch in product('甲乙丙', repeat=4):
        C = dict(zip(H, ch))
        if any(not 1 <= ch.count(e) <= 2 for e in '甲乙丙'): continue       # 每户如愿；每位企业家按要求选到1—2户
        if not (C['张'] == '甲' or C['王'] == '甲'): continue
        if sum(C[h] == '乙' for h in '王李赵') < 2: continue
        if not (C['张'] == '丙' or C['李'] == '丙'): continue
        M.append(C)
    judge('JS2019A-93', M, {'A': lambda C: C['张'] == '甲', 'B': lambda C: C['赵'] == '乙', 'C': lambda C: C['李'] == '丙', 'D': lambda C: C['王'] == '甲'}, 'must', 'B',
          note=str([''.join(f'{h}{C[h]}' for h in H) for C in M]))

def js2021a_94():
    M = []
    for p in permutations(['企业家', '大学教师', '歌手', '会计师']):
        J = dict(zip('甲乙丙丁', p))
        pred = {'甲': J['乙'] != '歌手', '乙': J['丙'] == '会计师', '丙': J['丁'] != '企业家', '丁': J['乙'] != '大学教师'}
        if all(pred[x] == (J[x] == '会计师') for x in '甲乙丙丁'): M.append(J)      # 只有会计师的预言正确
    opts = {'A': '企业家、大学教师、歌手、会计师', 'B': '大学教师、歌手、企业家、会计师', 'C': '企业家、歌手、会计师、大学教师', 'D': '会计师、大学教师、歌手、企业家'}
    judge('JS2021A-94', M, {k: (lambda L: (lambda J: J == L))(dict(zip('甲乙丙丁', v.split('、')))) for k, v in opts.items()}, 'must', 'D')
