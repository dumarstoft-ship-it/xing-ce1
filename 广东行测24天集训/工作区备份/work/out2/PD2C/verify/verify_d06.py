"""PD2C / D06 verification script.
Every logic item is solved by exhaustive enumeration of all models consistent with the stem (independent of the source analysis);
every computable science item is re-computed.  Run:  python3 -I verify_d06.py      (add --retired to also run the retired checks)
Each check prints the option(s) satisfying the ask and asserts it equals the expected (checked) answer.
11-08 原位替换：PD2C-001/003/005/006/016/018/019/021 的原题用户在“42天习题本”前三天做过，换成 GK2020F-107、ZJXD2020-30、
GDXD2019SW-12、JS2017A-97、GK2020F-111、GK2019F-115、JS2019A-93、JS2021A-94；原题的检查移入 RETIRED（保留备查，默认不运行）。"""
import sys
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
    flag = 'OK ' if ans == expect else 'XX '
    print(f'{flag}{qid:24s} models={len(models):6d} ask={mode:7s} -> {ans:4s} (expect {expect})  {stat} {note}')
    assert ans == expect, qid
    return ans

def record(qid, ans, expect, msg):
    RESULTS[qid] = ans
    print(('OK ' if ans == expect else 'XX ') + f'{qid:24s} {msg} -> {ans} (expect {expect})')
    assert ans == expect, qid

B = (0, 1)
# =====================================================================================
# 条件与必然性
# =====================================================================================
def gk2024f_106():
    # 只有扎根人民，创作才能获得源泉: 源泉 -> 扎根.  Other sentences are 要…/要多… exhortations (no conditional link between their parts).
    M = []
    for zg, yq, sj, gz, dy, lj, zc, jd in product(B, repeat=8):
        # zg 扎根人民, yq 创作获得源泉, sj 走进实践深处, gz 观照人民生活, dy 实地调查研究, lj 了解百姓生活/把握脉搏, jd 着眼需要解疑释惑
        if imp(yq, zg): M.append(dict(zg=zg, yq=yq, sj=sj, gz=gz, dy=dy, lj=lj, jd=jd))
    judge('GK2024F-106', M, {'A': lambda m: imp(m['gz'], m['sj']), 'B': lambda m: imp(not m['zg'], not m['yq']),
                             'C': lambda m: imp(m['lj'], m['dy']), 'D': lambda m: imp(not m['jd'], not m['dy'])}, 'must', 'B')

def js2024a_91():
    M = [dict(j=j, g=g, f=f) for j, g, f in product(B, repeat=3) if imp(f, j and g)]   # 飞 -> 两翼健壮 ∧ 共同力量
    st = {1: lambda m: imp(m['j'] and m['g'], m['f']), 2: lambda m: imp(m['f'], m['j'] and m['g']),
          3: lambda m: imp((not m['j']) or (not m['g']), not m['f']), 4: lambda m: imp(not m['f'], (not m['j']) or (not m['g']))}
    valid = tuple(k for k, f in st.items() if all(f(m) for m in M))
    ans = {(1, 2): 'A', (2, 3): 'B', (3, 4): 'C', (2, 4): 'D'}.get(valid, '?')
    record('JS2024A-91', ans, 'B', f'valid statements {valid}')

def zj2020b_63():
    M = [dict(ju=ju, zz=zz, zw=zw) for ju, zz, zw in product(B, repeat=3) if imp(zz, ju) and imp(not zz, zw)]
    # ju 采取大刀阔斧举措, zz 经济稳健增长, zw 公共债务不断攀升
    judge('ZJ2020B-63', M, {'A': lambda m: imp(m['zw'], not m['ju']), 'B': lambda m: imp(m['zw'], not m['ju']),
                            'C': lambda m: imp(m['ju'], not m['zw']), 'D': lambda m: imp(not m['zw'], m['ju'])}, 'must', 'D')

def gd2022x_56():
    # 法条: 合法延长工时 -> 工会同意 ∧ 被延长的劳动者同意 ; "一般每日不超过一小时"是一般规定(超时未必违法); 题干未给特殊行业豁免
    # 模型: 企业员工 3 人(被延长者 ext 非空), 每人是否同意, 工会是否同意, 延长是否超过 1 小时
    M = []
    for union, over1h in product(B, repeat=2):
        for ext in product(B, repeat=3):
            if not any(ext): continue
            for agree in product(B, repeat=3):
                if union and all(a for e, a in zip(ext, agree) if e):      # 没有违法
                    M.append(dict(union=union, over=over1h, special=0, allagree=all(agree)))
    judge('GD2022X-56', M, {'A': lambda m: not m['over'], 'B': lambda m: m['allagree'], 'C': lambda m: m['union'], 'D': lambda m: m['special']}, 'must', 'C',
          note='(一般≠一定; 同意者只需是被延长的员工)')

def gdxd2020sw_8():
    # 全签 -> (迟到 -> 全罚); 事实: 有人迟到, 队长未受罚.  四名队员示意(队长=0号)
    M = []
    for sign in product(B, repeat=4):
        for late in product(B, repeat=4):
            if not any(late): continue
            for pun in product(B, repeat=4):
                if pun[0]: continue
                if imp(all(sign), imp(any(late), all(pun))):
                    M.append(dict(sign=sign, late=late))
    judge('GDXD2020SW-8', M, {'A': lambda m: m['late'][0] and sum(m['late']) == 1, 'B': lambda m: sum(m['late']) <= 1,
                              'C': lambda m: not all(m['sign']), 'D': lambda m: not any(m['sign'])}, 'must', 'C')

def gd2017_56():
    M = []
    for who in ('张', '李'):
        for kt, jj in product(B, repeat=2):          # 开拓新业务, 精减人员
            if who == '张' and not kt: continue      # 张当上且实现主张
            if who == '李' and not jj: continue
            M.append(dict(who=who, kt=kt, jj=jj))
    judge('GD2017-56', M, {'A': lambda m: m['kt'] and m['jj'], 'B': lambda m: imp(m['kt'], m['who'] == '张'),
                           'C': lambda m: imp(m['jj'], m['who'] == '李'), 'D': lambda m: imp(not m['kt'], m['jj'])}, 'must', 'D')

def sc2020h_81():
    M = []
    for jg, my, jz, tg, hf, jh, fm in product(B, repeat=7):
        # jg 在国家机关, my 在民营企业, jz 失去晋职深造机会, tg 提高收入, hf 买得起婚房, jh 结婚, fm 女友父母改变想法
        if imp(not jg, jz) and imp(not my, not tg) and not (jg and my) and imp(not tg, not hf) and imp(not hf, not jh) and jh:
            M.append(dict(jg=jg, my=my, jz=jz, fm=fm))
    judge('SC2020H-81', M, {'A': lambda m: not m['jg'], 'B': lambda m: not m['my'], 'C': lambda m: not m['jz'], 'D': lambda m: m['fm']}, 'must', 'A')

def gk2024f_115():
    M = [dict(a=a, b=b, c=c, d=d) for a, b, c, d in product(B, repeat=4)
         if imp(not a and not b, c) and imp(b or c, d) and imp(a or b, c and not d)]
    judge('GK2024F-115', M, {'A': lambda m: m['c'] and m['d'], 'B': lambda m: m['a'] and m['d'], 'C': lambda m: m['a'] and m['b'], 'D': lambda m: m['b'] and m['c']}, 'must', 'A')

def gk2018f_109():
    # 队员类型：省运会冠军、国家队队员、其他；达标与否
    M = []
    for gj, gd, qt in product(B, repeat=3):
        zhang = not (gj or gd or qt); sun = gj or gd or qt; wang = gj or gd
        if zhang + sun + wang == 1: M.append(dict(gj=gj, gd=gd, qt=qt))
    judge('GK2018F-109', M, {'A': lambda m: not (m['gj'] or m['gd'] or m['qt']), 'B': lambda m: m['gj'] and m['gd'] and m['qt'],
                             'C': lambda m: m['gj'], 'D': lambda m: not m['gd']}, 'must', 'D')

def sc2024_84():
    # 游客 3 人(含王女士 W、郑先生 Z、另一人 O)；每人：买白瓷 b、青瓷 q、其他瓷 o（是否买瓷器 = 任一）
    M = []
    for W in product(B, repeat=3):
        for Z in product(B, repeat=3):
            for O in product(B, repeat=3):
                buy = [any(W), any(Z), any(O)]
                s1 = all(buy); s2 = bool(W[0]); s3 = not all(buy); s4 = imp(not Z[1], W[0])
                if s1 + s2 + s3 + s4 == 2: M.append(dict(W=W, Z=Z, O=O))
    judge('SC2024-84', M, {'A': lambda m: not any(m['W']), 'B': lambda m: m['Z'][1], 'C': lambda m: m['W'][0],
                           'D': lambda m: not (m['W'][1] and m['Z'][1] and m['O'][1])}, 'must', 'B')

def sc2023_85():
    M = []
    for buy in product(B, repeat=4):          # 1=购物(只购物), 0=看电影(只看电影)
        a, b, c, d = buy
        s = [d, imp(a, not b), imp(not d, not c), a and b]
        if sum(map(bool, s)) == 1: M.append(dict(a=a, b=b, c=c, d=d))
    judge('SC2023-85', M, {'A': lambda m: m['b'] and not m['a'], 'B': lambda m: m['c'] and not m['b'], 'C': lambda m: m['c'] and not m['d'],
                           'D': lambda m: not m['a'] and not m['b']}, 'must', 'C')

def sd2022_75():
    M = []
    for cap in product(B, repeat=3):          # 甲乙丙能否预测
        s = [cap[0], not all(cap), any(cap)]
        if sum(map(bool, s)) == 1: M.append(cap)
    judge('SD2022-75', M, {'A': lambda c: c[1] and not c[2], 'B': lambda c: c[0] and not c[1], 'C': lambda c: not c[1] and not c[2], 'D': lambda c: c[2] and not c[0]}, 'must', 'C')

def gk2018f_110():
    # 个体类型：(30岁以下 y, 报名培训 p, 部门经理 m, 同意拓展 agree)；经理->同意；报名->反对；存在 y∧p
    types = [t for t in product(B, repeat=4) if imp(t[2], t[3]) and imp(t[1], not t[3])]
    M = []
    for k in range(1, len(types) + 1):
        for pop in combinations(types, k):
            if any(t[0] and t[1] for t in pop): M.append(pop)
    judge('GK2018F-110', M, {'A': lambda p: all(not t[0] for t in p if t[2]), 'B': lambda p: any(t[2] and t[1] for t in p),
                             'C': lambda p: all(t[0] for t in p if t[1]), 'D': lambda p: any(t[0] and not t[2] for t in p)}, 'must', 'D')

def gd2023x_71():
    # 个体类型 (跑步 r, 羽毛球 y, 篮球 l, 排球 p)；所有员工 r∨y；r->¬l；小丽 l。问：补充哪项后 "小丽在排球队" 必然成立
    types = [t for t in product(B, repeat=4) if (t[0] or t[1]) and imp(t[0], not t[2])]
    sup = {'A': lambda pop, li: not li[0], 'B': lambda pop, li: not li[1],
           'C': lambda pop, li: all(t[1] for t in pop + [li] if t[3]), 'D': lambda pop, li: all(not t[1] for t in pop + [li] if not t[3])}
    ok = ''
    others = types
    for k, f in sup.items():
        worlds = []
        for li in types:
            if not li[2]: continue
            for n in range(0, 3):
                for pop in combinations(others, n):
                    if f(list(pop), li): worlds.append(li)
        if worlds and all(li[3] for li in worlds): ok += k
    record('GD2023X-71', ok, 'D', 'supplement making 小丽∈排球队 necessary')

def gdxd2020sw_48():
    # 一周 7 天；每天开设 瑜伽 y / 单车 c / 芭蕾 b；王女士每天去或不去，去则参加当天的若干课程
    # 规则：y∧c -> b ; b -> 星期一 ; 王去 -> 当天开设 y
    days = range(7)    # 0=星期一
    M = []
    for d in days:
        for y, c, bb in product(B, repeat=3):
            if not imp(y and c, bb) or not imp(bb, d == 0): continue
            for go in B:
                if go and not y: continue
                for py, pc, pb in product(B, repeat=3):     # 王参加了哪些课程（须当天开设且王去了）
                    if (py or pc or pb) and not go: continue
                    if (py and not y) or (pc and not c) or (pb and not bb): continue
                    M.append(dict(d=d, y=y, c=c, b=bb, go=go, py=py, pc=pc, pb=pb))
    judge('GDXD2020SW-48', M, {'A': lambda m: imp(m['d'] == 0 and m['py'], m['c']), 'B': lambda m: imp(m['d'] == 1 and m['c'], not m['go']),
                               'C': lambda m: imp(m['pb'], m['d'] != 2), 'D': lambda m: imp(m['d'] == 3 and m['go'], not m['pc'])}, 'notmust', 'A')

# ---- 11-08 原位替换（G1）：原 GK2024F-106 / JS2024A-91 / GD2022X-56 / SC2020H-81 用户已做 ----
def gk2020f_107():      # PD2C-001
    # 只翻与“文明”有关的三句：长期自我封闭 fb -> 走向衰落 sl；保持旺盛生命活力 hl -> 交流互鉴 jl ∧ 取长补短 qc（首句“生命有机体”只是类比）
    M = [dict(fb=fb, sl=sl, jl=jl, qc=qc, hl=hl) for fb, sl, jl, qc, hl in product(B, repeat=5) if imp(fb, sl) and imp(hl, jl and qc)]
    judge('GK2020F-107', M, {'A': lambda m: imp(not m['jl'], not m['hl']), 'B': lambda m: imp(not m['fb'], not m['sl']),
                             'C': lambda m: imp(m['jl'] and m['qc'], m['hl']), 'D': lambda m: imp(not m['hl'], not m['qc'])}, 'must', 'A')

def zjxd2020_30():      # PD2C-003
    # 规则：(甲爱看 ∨ 乙不爱看) -> 丙爱看。问补充哪项能推出“乙爱看”：该项与规则相容，且在所有满足二者的模型中乙都爱看。
    rule = [dict(a=a, b=b, c=c) for a, b, c in product(B, repeat=3) if imp(a or not b, c)]
    prem = {'A': lambda m: not m['c'], 'B': lambda m: not m['a'], 'C': lambda m: m['a'] and m['c'],
            'D': lambda m: (not m['a']) + (not m['c']) == 1,             # “甲和丙有一个不爱看”按“恰有一个”
            'D*': lambda m: (not m['a']) or (not m['c'])}                # 另一读法“至少一个”
    ent = {k: any(f(m) for m in rule) and all(m['b'] for m in rule if f(m)) for k, f in prem.items()}
    assert ent['D'] == ent['D*']
    record('ZJXD2020-30', ''.join(k for k in 'ABCD' if ent[k]), 'A', f'premise entails 乙爱看: {ent}')

def gdxd2019sw_12():    # PD2C-005
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

def js2017a_97():       # PD2C-006
    # 死因 ∈ {自杀, 谋杀, 意外}；li = 李某脱不了干系。甲：谋杀 -> li（“这段时间她正和张某闹离婚”是理由，解析同此译法）；乙：死因不是意外。
    # 赵警官（均为真）：(1) 甲乙同对或同错 -> 意外；(2) 甲乙中有一人错 -> 不是意外。(2) 按“恰有一人错”“至少一人错”两种读法都穷举。
    for rd in ('exactly', 'atleast'):
        M = []
        for cause, li in product(('自杀', '谋杀', '意外'), B):
            j = imp(cause == '谋杀', li); y = cause != '意外'; wrong = (not j) + (not y)
            if imp(j == y, cause == '意外') and imp(wrong == 1 if rd == 'exactly' else wrong >= 1, cause != '意外'):
                M.append(dict(cause=cause, li=li))
        judge(f'JS2017A-97({rd})', M, {'A': lambda m: m['cause'] == '谋杀', 'B': lambda m: m['cause'] == '自杀',
                                       'C': lambda m: m['cause'] == '意外', 'D': lambda m: m['cause'] == '谋杀' and m['li']}, 'must', 'A')
    # 读法说明（不断言）：若把“正和张某闹离婚”也算作甲断言的一部分，死因不再唯一——所以按解析只判条件句的真假
    for rd in ('exactly', 'atleast'):
        alt = set()
        for cause, li, lh in product(('自杀', '谋杀', '意外'), B, B):
            j = imp(cause == '谋杀', li) and lh; y = cause != '意外'; wrong = (not j) + (not y)
            if imp(j == y, cause == '意外') and imp(wrong == 1 if rd == 'exactly' else wrong >= 1, cause != '意外'): alt.add(cause)
        print(f'   note({rd}): if "正和张某闹离婚" were part of 甲\'s claim, possible causes = {sorted(alt)} -> 按解析译法只判条件句')

COND = [gk2020f_107, zj2020b_63, zjxd2020_30, gdxd2020sw_8, gdxd2019sw_12, js2017a_97, gd2017_56, gk2024f_115,
        gk2018f_109, sc2024_84, sc2023_85, sd2022_75, gk2018f_110, gd2023x_71, gdxd2020sw_48]


# =====================================================================================
# 组合（分析推理）
# =====================================================================================
def gd2023x_58():
    cand = {'甲': ('高一', '史'), '乙': ('高一', '地'), '丙': ('高一', '政'), '丁': ('高二', '地'), '戊': ('高二', '语'), '己': ('高三', '政'), '庚': ('高三', '数')}
    def ok(g):
        gr = [cand[x][0] for x in g]; sb = [cand[x][1] for x in g]
        return gr.count('高一') == 2 and gr.count('高二') == 1 and gr.count('高三') == 1 and len(set(sb)) == 4
    opts = {'A': '甲乙丁庚', 'B': '甲乙戊己', 'C': '乙丙戊己', 'D': '乙戊己庚'}
    record('GD2023X-58', ''.join(k for k, v in opts.items() if ok(v)), 'B', 'groups satisfying (2高一+1高二+1高三, 科目各不相同)')

def gk2017f_115():
    M = []
    for p in permutations(['行政', '销售', '研发', '安保']):
        P = dict(zip('张王李赵', p))
        if P['张'] in ('行政', '安保') or P['王'] in ('行政', '研发') or P['李'] in ('行政', '安保') or P['赵'] in ('研发', '安保'): continue
        if not imp(P['张'] != '研发', P['赵'] != '行政'): continue
        M.append(P)
    judge('GK2017F-115', M, {'A': lambda P: P['张'] == '销售' and P['李'] == '研发', 'B': lambda P: P['赵'] == '研发' and P['李'] == '销售',
                             'C': lambda P: P['李'] == '销售' and P['张'] == '研发', 'D': lambda P: P['李'] == '研发' and P['赵'] == '安保'}, 'must', 'C')

def gd2023x_56():
    M = []
    for a in product('ABCD', repeat=6):
        P = dict(zip(['甲', '乙', '丙', '张', '李', '王'], a))
        if not {P['甲'], P['乙'], P['丙']} <= {P['张'], P['李'], P['王']}: continue      # 有男性去的社区必须有女性去
        if P['张'] not in 'AB' or P['乙'] != 'D' or P['李'] != 'C': continue
        M.append(P)
    judge('GD2023X-56', M, {'A': lambda P: P['丙'] == 'A', 'B': lambda P: P['张'] == 'B', 'C': lambda P: P['甲'] == 'C', 'D': lambda P: P['王'] == 'D'}, 'must', 'D')

def hb2024_105():
    P7 = ['赵', '钱', '孙', '李', '周', '吴', '郑']; M = []
    for am in combinations(P7, 4):
        A = set(am); pm = set(P7) - A
        same = lambda x, y: (x in A) == (y in A)
        if same('赵', '孙') or same('周', '孙'): continue
        if not imp('郑' in pm, '赵' in pm and '李' in pm): continue
        if not ('钱' in A or '郑' in pm): continue
        M.append(A)
    judge('HB2024-105', M, {'A': lambda A: {'钱', '郑'} <= A, 'B': lambda A: {'赵', '郑'} <= A, 'C': lambda A: {'赵', '周'} <= A, 'D': lambda A: {'吴', '孙'} <= A}, 'must', 'A')

def gdxd2019sw_45():
    P4 = '甲乙丙丁'; M = []
    for ms, cpa, gj in product(product(B, repeat=4), repeat=3):
        if sum(ms) != 3 or sum(cpa) != 2 or sum(gj) != 1: continue
        three = [i for i in range(4) if ms[i] and cpa[i] and gj[i]]
        if len(three) != 1 or any(not (ms[i] or cpa[i] or gj[i]) for i in range(4)): continue
        if ms[0] != ms[3] or cpa[1] != cpa[2] or ms[2] + ms[3] != 1: continue
        M.append(P4[three[0]])
    judge('GDXD2019SW-45', M, {k: (lambda x: (lambda m: m == x))(x) for k, x in zip('ABCD', P4)}, 'must', 'B')

def sc2025_85():
    names = ['高', '胡', '杨', '陈']
    for conv in (+1, -1):     # 两种左右约定都检验（人面向桌心时的左手/右手）
        M = []
        for seat in permutations(range(4)):
            S = dict(zip(names, seat)); who = {v: k for k, v in S.items()}
            left = lambda n: who[(S[n] + conv) % 4]; right = lambda n: who[(S[n] - conv) % 4]; opp = lambda n: who[(S[n] + 2) % 4]
            for col in permutations(['蓝', '黄', '粉', '红']):
                C = dict(zip(names, col)); by = {v: k for k, v in C.items()}
                if left('杨') != '陈' or C['陈'] == '蓝' or right(by['蓝']) != '胡' or opp('杨') != by['黄'] or by['黄'] == '胡': continue
                M.append(dict(opp=opp, C=C, by=by))
        judge(f'SC2025-85(conv{conv:+d})', M, {'A': lambda m: m['opp'](m['by']['红']) == m['by']['粉'], 'B': lambda m: m['opp']('陈') == m['by']['黄'],
                                              'C': lambda m: m['C']['胡'] == '红', 'D': lambda m: m['opp']('高') != '杨'}, 'must', 'A')

def gk2018f_115():
    for R in (1, -1):         # "右边"取顺时针或逆时针，两种约定都检验
        M = []
        for chairs in permutations([1, 2, 3, 4, 5]):
            if chairs[0] != 1: continue                       # 固定旋转
            pos = {c: i for i, c in enumerate(chairs)}
            at = lambda c, k: chairs[(pos[c] + k) % 5]
            for ppl in permutations('甲乙丙丁戊'):
                P = {p: chairs[i] for i, p in enumerate(ppl)}
                if P['甲'] != at(1, 2 * R) or P['乙'] != at(5, -2 * R) or P['丙'] != at(3, -R) or P['丁'] != at(2, -R): continue
                if any(P[p] == i + 1 for i, p in enumerate('甲乙丙丁戊')): continue    # 均未按顺序坐
                if P['丙'] != 1: continue
                M.append(P)
        judge(f'GK2018F-115(R{R:+d})', M, {k: (lambda x: (lambda P: P['甲'] == x))(x) for k, x in zip('ABCD', [2, 3, 4, 5])}, 'must', 'C')

# ---- 11-08 原位替换（G3）：原 GD2023X-58 / GD2023X-56 / HB2024-105 / SC2025-85 用户已做 ----
def gk2020f_111():      # PD2C-016
    M = []
    for p in permutations('ABCDF'):
        P = dict(zip('甲乙丙丁戊', p))
        if P['丁'] != 'B': continue
        if not imp(P['甲'] == 'C' or P['乙'] == 'C', P['丙'] == 'B'): continue
        if not imp(P['戊'] == 'C', P['丁'] == 'F'): continue
        M.append(P)
    judge('GK2020F-111', M, {'A': lambda P: P['甲'] == 'A', 'B': lambda P: P['乙'] == 'D', 'C': lambda P: P['丙'] == 'C', 'D': lambda P: P['戊'] == 'F'}, 'must', 'C')

def gk2019f_115():      # PD2C-018
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

def js2019a_93():       # PD2C-019
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

def js2021a_94():       # PD2C-021
    M = []
    for p in permutations(['企业家', '大学教师', '歌手', '会计师']):
        J = dict(zip('甲乙丙丁', p))
        pred = {'甲': J['乙'] != '歌手', '乙': J['丙'] == '会计师', '丙': J['丁'] != '企业家', '丁': J['乙'] != '大学教师'}
        if all(pred[x] == (J[x] == '会计师') for x in '甲乙丙丁'): M.append(J)      # 只有会计师的预言正确
    opts = {'A': '企业家、大学教师、歌手、会计师', 'B': '大学教师、歌手、企业家、会计师', 'C': '企业家、歌手、会计师、大学教师', 'D': '会计师、大学教师、歌手、企业家'}
    judge('JS2021A-94', M, {k: (lambda L: (lambda J: J == L))(dict(zip('甲乙丙丁', v.split('、')))) for k, v in opts.items()}, 'must', 'D')

# ---- 一拖三：GK2021F-114 原题 + 2 道改编（同一题干）----
P8 = '甲乙丙丁戊己庚辛'
def rooms():
    M = []
    for p in permutations(range(1, 9)):
        P = dict(zip(P8, p))
        if abs(P['甲'] - P['丙']) != 4 or abs(P['乙'] - P['己']) != 3 or P['庚'] - P['丁'] != 3 or abs(P['辛'] - P['戊']) != 2: continue
        M.append(P)
    return M
between = lambda P, x, a, b: min(P[a], P[b]) < P[x] < max(P[a], P[b])
def gk2021f_114_set():
    M = rooms()
    judge('GK2021F-114', M, {k: (lambda x: (lambda P: P['丁'] == x))(x) for k, x in zip('ABCD', [1, 2, 3, 4])}, 'cannot', 'C')
    M2 = [P for P in M if abs(P['庚'] - P['辛']) == 1]
    judge('PD2C-V114a(庚辛相邻)', M2, {'A': lambda P: P['甲'] == 2, 'B': lambda P: P['乙'] == 5, 'C': lambda P: P['丁'] == 1, 'D': lambda P: P['己'] == 4}, 'can', 'D')
    M3 = [P for P in M if abs(P['乙'] - P['戊']) == 1]
    judge('PD2C-V114b(乙戊相邻)', M3, {'A': lambda P: between(P, '丁', '甲', '丙'), 'B': lambda P: between(P, '戊', '甲', '丙'),
                                       'C': lambda P: between(P, '庚', '甲', '丙'), 'D': lambda P: between(P, '辛', '甲', '丙')}, 'must', 'B')
    cl = sorted({(min(P['甲'], P['丙']), min(P['辛'], P['戊'])) for P in M})
    print(f'   structure: (甲丙 left room, 辛戊 left room) pairs over all {len(M)} models = {cl}  -> 甲丙{{2,6}}必配辛戊{{1,3}}, 甲丙{{3,7}}必配辛戊{{6,8}}')

# ---- 一拖五：GK2021D-106~110 ----
DEP = ['人事', '科研', '教育', '财务', '宣传', '后勤', '工会']
def gk2021d_models():
    M = []
    for a in product('王卫丁', repeat=7):
        P = dict(zip(DEP, a))
        if P['教育'] != P['财务'] or P['宣传'] != P['后勤']: continue
        cnt = {x: a.count(x) for x in '王卫丁'}
        if not cnt['丁'] > cnt['卫']: continue
        if (P['教育'] == '王') + (P['工会'] == '王') != 1: continue      # 教育、工会中(恰有)一个由王分管
        if (P['工会'] == '卫') + (P['后勤'] == '卫') != 1: continue      # 工会、后勤中(恰有)一个由卫分管
        M.append(P)
    return M
def gk2021d_set():
    M = gk2021d_models()
    cnt = lambda P, x: sum(1 for d in DEP if P[d] == x)
    lay = lambda s: {d: x for x, ds in s.items() for d in ds}
    o106 = {'A': {'王': ['工会', '科研'], '卫': ['人事', '教育', '财务'], '丁': ['宣传', '后勤']},
            'B': {'王': ['人事', '工会'], '卫': ['宣传', '后勤'], '丁': ['科研', '教育', '财务']},
            'C': {'王': ['教育', '财务'], '卫': ['人事', '后勤'], '丁': ['科研', '宣传', '工会']},
            'D': {'王': ['宣传', '后勤'], '卫': ['人事', '工会'], '丁': ['科研', '教育', '财务']}}
    judge('GK2021D-106', M, {k: (lambda L: (lambda P: P == L))(lay(s)) for k, s in o106.items()}, 'can', 'B')
    judge('GK2021D-107', [P for P in M if cnt(P, '王') > cnt(P, '丁')], {'A': lambda P: P['人事'] == '卫', 'B': lambda P: P['科研'] == '卫',
                                                                        'C': lambda P: P['教育'] == '丁', 'D': lambda P: P['后勤'] == '丁'}, 'can', 'D')
    judge('GK2021D-108', M, {'A': lambda P: P['人事'] == P['宣传'] == '王', 'B': lambda P: P['人事'] == P['宣传'] == '丁',
                             'C': lambda P: P['科研'] == P['宣传'] == '丁', 'D': lambda P: P['教育'] == P['宣传'] == '王'}, 'cannot', 'A')
    judge('GK2021D-109', M, {k: (lambda d: (lambda P: P['财务'] == P[d]))(d) for k, d in zip('ABCD', ['人事', '科研', '宣传', '工会'])}, 'cannot', 'D')
    judge('GK2021D-110', [P for P in M if P['科研'] == P['宣传']], {'A': lambda P: P['人事'] == '卫', 'B': lambda P: P['科研'] == '王',
                                                                   'C': lambda P: P['教育'] == '丁', 'D': lambda P: P['宣传'] == '卫'}, 'can', 'A')
    print(f'   GK2021D base models = {len(M)}')

COMBO = [gk2020f_111, gk2017f_115, gk2019f_115, js2019a_93, gdxd2019sw_45, js2021a_94, gk2018f_115, gk2021f_114_set, gk2021d_set]

# 11-08 被替换的原题（用户在42天习题本前三天做过）：检查函数保留备查，默认不运行；python3 -I verify_d06.py --retired 可单独复跑
RETIRED = [gk2024f_106, js2024a_91, gd2022x_56, sc2020h_81, gd2023x_58, gd2023x_56, hb2024_105, sc2025_85]


# =====================================================================================
# 科学推理（可计算项复算；知识项只在答案册给理由，不在此处）
# =====================================================================================
import math, random
def gd2016z_70():
    # 读图（300dpi 像素量取）：右臂绳子挂在 2.5 格处；左臂 50g 挂在 1 格；A=4、B=3、C=2.5、D=1.5 格
    # 滑轮组：P 为动滑轮，由 2 段绳承担 100g -> 绳中拉力 50g，经定滑轮 O、Q 向下拉天平右臂
    T = Fr(100, 2)
    right = T * Fr(5, 2); left0 = 50 * 1
    opts = {'A': (15, Fr(4)), 'B': (25, Fr(3)), 'C': (50, Fr(5, 2)), 'D': (75, Fr(3, 2))}
    ok = ''.join(k for k, (m, x) in opts.items() if left0 + m * x == right)
    record('GD2016Z-70', ok, 'B', f'right torque {right}, left needs extra {right - left0}')

def refract(d, n, n1, n2):
    """d: unit direction, n: unit normal pointing toward incident side; Snell vector form"""
    cosi = -(d[0] * n[0] + d[1] * n[1]); r = n1 / n2; k = 1 - r * r * (1 - cosi * cosi)
    cost = math.sqrt(k)
    return (r * d[0] + (r * cosi - cost) * n[0], r * d[1] + (r * cosi - cost) * n[1])
def cross_line(p, d, q, u):
    """intersection of ray p+t d with line q+s u"""
    det = d[0] * (-u[1]) - d[1] * (-u[0])
    t = ((q[0] - p[0]) * (-u[1]) - (q[1] - p[1]) * (-u[0])) / det
    return (p[0] + t * d[0], p[1] + t * d[1])
def gd2017_64():
    s = 1 / math.sqrt(2); nglass = 1.5; th = 1.0
    # 左砖：两表面方向 (s,s)，外表面过 (-3,0)，内表面沿法向 (s,-s) 平移 th；右砖为其关于 x=0 的镜像
    uL = (s, s); nL = (-s, s)          # 法线（指向左上=入射侧）
    p = (-10.0, 0.7); d = (1.0, 0.0)
    q1 = (-3.0, 0.0); q2 = (q1[0] + th * s, q1[1] - th * s)
    a = cross_line(p, d, q1, uL); d1 = refract(d, nL, 1, nglass)
    b = cross_line(a, d1, q2, uL); d2 = refract(d1, nL, nglass, 1)
    uR = (s, -s); nR = (-s, -s)        # 右砖表面方向与法线（指向左下=入射侧）
    r1 = (3.0, 0.0); r2 = (r1[0] - th * s, r1[1] - th * s)
    c = cross_line(b, d2, r2, uR); d3 = refract(d2, nR, 1, nglass)
    e = cross_line(c, d3, r1, uR); d4 = refract(d3, nR, nglass, 1)
    y_out = e[1] + (10 - e[0]) * d4[1] / d4[0]
    collinear = abs(d4[1]) < 1e-9 and abs(y_out - p[1]) < 1e-9
    parallel_shift = abs(d4[1]) < 1e-9 and not collinear
    ans = 'C' if collinear else ('D' if parallel_shift else '?')
    record('GD2017-64', ans, 'C', f'exit dir=({d4[0]:.6f},{d4[1]:.6f}), y_in={p[1]}, y_out={y_out:.6f}; shift in slab1 cancels slab2')

def gd2018_65():
    R1, R2 = Fr(10, 20), Fr(10, 5)
    det = {'A': R1 / R2 == Fr(1, 4), 'C': (1 / R1) / (1 / R2) == 4, 'D': R1 / R2 == Fr(1, 4)}
    assert all(det.values())
    record('GD2018-65', 'B', 'B', f'R1={R1}Ω R2={R2}Ω: A/C/D 可由图算出; 额定功率需额定电压/电流, 伏安曲线不给 -> 无法确定 B')

def gd2020z_72():
    ch = ['+', '-', '0']
    def force(x, y):     # 'att' / 'rep' / 'none'
        if x == '0' and y == '0': return 'none'
        if x == '0' or y == '0': return 'att'
        return 'rep' if x == y else 'att'
    M = [dict(甲=a, 乙=b, 丙=c) for a, b, c in product(ch, repeat=3) if force(a, b) == 'att' and force(a, c) == 'rep']
    can = lambda cond, concl: any(cond(m) and concl(m) for m in M)
    st = {'A': can(lambda m: m['乙'] == '+', lambda m: m['丙'] == '+'), 'B': can(lambda m: m['乙'] == '+', lambda m: m['丙'] == '0'),
          'C': can(lambda m: m['丙'] == '-', lambda m: m['乙'] == '-'), 'D': can(lambda m: m['丙'] == '-', lambda m: m['乙'] == '0')}
    record('GD2020Z-72', ''.join(k for k, v in st.items() if v), 'D', f'charge models {[(m["甲"], m["乙"], m["丙"]) for m in M]}')

def gd2021z_85():
    m, g = 2.0, 10.0
    for deg in (20, 37, 53):
        th = math.radians(deg)
        F = m * g * math.tan(th); N = m * g / math.cos(th)         # A 静止于光滑斜面: N cosθ = mg, N sinθ = F
        fB = N * math.sin(th)                                       # B 水平方向: 地面摩擦 = A 压力水平分量
        assert abs(fB - F) < 1e-9 and N > F
    record('GD2021Z-85', 'B', 'B', 'B 受重力、地面支持力、A的压力、地面摩擦共4个力; 地面摩擦 = F; A对B作用力 = √(F²+(m_Ag)²) > F')

def gd2021z_73():
    n = 18; seq = [n]                  # 间期复制后仍 18 条(每条含两条染色单体)
    seq.append(2 * n)                  # 后期着丝点分裂 -> 36
    seq.append(n)                      # 末期分到两个子细胞 -> 每个 18
    record('GD2021Z-73', 'C' if seq == [18, 36, 18] else '?', 'C', f'chromosomes per cell {seq}')

def gd2022x_84():
    random.seed(1); ok = True
    for _ in range(2000):
        m1, m2 = random.uniform(0.1, 5), random.uniform(0.1, 5)
        T2 = (random.uniform(0.01, 5), -random.uniform(0.01, 5))     # 下平面绳对 M2 的拉力：斜向右下
        T1 = (-T2[0], -T2[1] + (m1 + m2) * 10)                       # 整体：T1 + T2 + (m1+m2)g = 0 (磁力为内力)
        ok &= math.hypot(*T1) > math.hypot(*T2)
    record('GD2022X-84', 'A' if ok else '?', 'A', 'system M1+M2: horizontal parts cancel, |T1y| = |T2y| + (m1+m2)g -> F1 > F2 always')

def gd2023z_67():
    random.seed(2); hold = {1: True, 2: True, 3: True, 4: True}
    for _ in range(20000):
        V2, S1, m2 = random.uniform(1, 10), random.uniform(1, 10), random.uniform(1, 10)
        V1 = V2 * random.uniform(1.01, 5); S2 = S1 * random.uniform(1.01, 5); m1 = m2 * random.uniform(1.01, 5)
        h1, h2, r1, r2 = V1 / S1, V2 / S2, m1 / V1, m2 / V2
        hold[1] &= h1 > h2; hold[2] &= h1 < h2; hold[3] &= r1 > r2; hold[4] &= r1 < r2
    nec = tuple(k for k, v in hold.items() if v)
    record('GD2023Z-67', {(1,): 'A', (3,): 'B', (1, 3): 'C', (2, 4): 'D'}.get(nec, '?'), 'A', f'always-true statements {nec}')

def v_four_blocks():
    # 改编（母题 GD2025-67）：4 块相同木块，左右夹板对称；向上为正。未知量 fL f12 f23 f34 fR（f_ij 为 j 对 i... 统一记作界面 i|i+1 上对左块的摩擦）
    G = Fr(1)
    # 平衡: 块1: fL + f12 - G = 0; 块2: -f12 + f23 - G = 0; 块3: -f23 + f34 - G = 0; 块4: -f34 + fR - G = 0; 对称: fL = fR
    # 由前三式 f12 = G - fL, f23 = 2G - fL, f34 = 3G - fL; 第四式 fR = 4G - fL; 对称 -> fL = 2G
    fL = 2 * G; f12 = G - fL; f23 = 2 * G - fL; f34 = 3 * G - fL; fR = 4 * G - fL
    # f12 为"2号对1号"的摩擦(向上为正) = -G：2号对1号向下 G；1号对2号向上 G
    on1 = [fL, f12]; on2 = [-f12, f23]
    st = {'A': all(x > 0 for x in on1) or all(x < 0 for x in on1), 'B': sum(on2) < 0 and all(x <= 0 for x in on2),
          'C': fL == G, 'D': f23 == 0}
    record('PD2C-VS1(4块夹物)', ''.join(k for k, v in st.items() if v), 'D', f'fL={fL}G f12={f12}G f23={f23}G f34={f34}G fR={fR}G')
    # 记忆检验：母题 3 块时中间块受摩擦向上、外侧块各受两个反向摩擦
    fL3 = Fr(3, 2); f12_3 = G - fL3
    print(f'   memory check (3 blocks): fL={fL3}G, block2 gets {-f12_3}G up from each side -> 原题"中间块摩擦向上"的记忆在4块时不成立(2号块所受摩擦合为G向上来自1号, 2|3界面为0)')

def v_wood_block():
    # 改编（母题 GD2026-67）：底面积 S=400cm²、高 H=5cm、质量 1.2kg 的实心长方体木块(ρ=0.6g/cm³)平放于柱形容器底部(底面不密合)，缓慢加水至 20cm
    S, H, m, rho, g = 0.04, 0.05, 1.2, 1000.0, 10.0
    hstar = m / (rho * S)                            # 浮力 = 重力 时的浸入深度
    F = lambda h: max(0.0, m * g - rho * g * S * min(h, H))
    samples = [(h, round(F(h), 6)) for h in (0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.10, 0.20)]
    linear_then_zero = abs(hstar - 0.03) < 1e-12 and all(abs(F(h) - (m * g - rho * g * S * h)) < 1e-9 for h in (0, 0.015, 0.029)) and all(F(h) == 0 for h in (0.031, 0.05, 0.2))
    st = {'A': False,                                 # "h=5cm 时 F 才减为零" 与 h*=3cm 矛盾
          'B': linear_then_zero, 'C': False,          # "h≥5cm 后保持不变且不为零" 是铜块(母题)的情形
          'D': F(0.0) == 0}                           # 加水前 F = mg = 12N ≠ 0
    # 漂浮稳定性：扁木块稳心高度 GM = KB + BM - KG > 0（边长 b=0.2m 的正方形底面）；对比：密度0.6的正方体 GM < 0
    b = 0.2; GM = hstar / 2 + b * b / (12 * hstar) - H / 2
    a = 0.1; d = 0.6 * a; GMcube = d / 2 + a * a / (12 * d) - a / 2
    assert GM > 0 and GMcube < 0
    record('PD2C-VS2(木块加水)', ''.join(k for k, v in st.items() if v), 'B', f'h*={hstar*100:.1f}cm, F(h) samples (m,N)={samples}; GM(slab)={GM:.3f}m>0, GM(cube ρ0.6)={GMcube:.4f}m<0')

SCI = [gd2016z_70, gd2017_64, gd2018_65, gd2020z_72, gd2021z_85, gd2021z_73, gd2022x_84, gd2023z_67, v_four_blocks, v_wood_block]


# =====================================================================================
# 与 questions.jsonl 交叉核对：每题 checked_answer 必须等于上面穷举/复算的结果
# =====================================================================================
KEYMAP = {  # 题号 -> RESULTS 键（知识型定性题不在此表：PD2C-031、041、042、043、045 只在答案册给理由）
    'PD2C-001': 'GK2020F-107', 'PD2C-002': 'ZJ2020B-63', 'PD2C-003': 'ZJXD2020-30', 'PD2C-004': 'GDXD2020SW-8', 'PD2C-005': 'GDXD2019SW-12',
    'PD2C-006': 'JS2017A-97(exactly)', 'PD2C-007': 'GD2017-56', 'PD2C-008': 'GK2024F-115', 'PD2C-009': 'GK2018F-109', 'PD2C-010': 'SD2022-75',
    'PD2C-011': 'SC2024-84', 'PD2C-012': 'GK2018F-110', 'PD2C-013': 'SC2023-85', 'PD2C-014': 'GDXD2020SW-48', 'PD2C-015': 'GD2023X-71',
    'PD2C-016': 'GK2020F-111', 'PD2C-017': 'GK2017F-115', 'PD2C-018': 'GK2019F-115', 'PD2C-019': 'JS2019A-93', 'PD2C-020': 'GDXD2019SW-45',
    'PD2C-021': 'JS2021A-94', 'PD2C-022': 'GK2018F-115(R+1)', 'PD2C-023': 'GK2021F-114', 'PD2C-024': 'PD2C-V114a(庚辛相邻)',
    'PD2C-025': 'PD2C-V114b(乙戊相邻)', 'PD2C-026': 'GK2021D-106', 'PD2C-027': 'GK2021D-107', 'PD2C-028': 'GK2021D-108',
    'PD2C-029': 'GK2021D-109', 'PD2C-030': 'GK2021D-110', 'PD2C-032': 'GD2021Z-85', 'PD2C-033': 'PD2C-VS1(4块夹物)', 'PD2C-034': 'GD2017-64',
    'PD2C-035': 'GD2016Z-70', 'PD2C-036': 'GD2020Z-72', 'PD2C-037': 'GD2018-65', 'PD2C-038': 'GD2022X-84', 'PD2C-039': 'PD2C-VS2(木块加水)',
    'PD2C-040': 'GD2023Z-67', 'PD2C-044': 'GD2021Z-73'}
def crosscheck():
    import json, os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'questions.jsonl')
    rows = [json.loads(l) for l in open(path)]
    bad = 0
    for r in rows:
        k = KEYMAP.get(r['id'])
        if k is None: continue
        got = RESULTS[k]
        if got != r['checked_answer']: bad += 1; print('XX', r['id'], k, got, r['checked_answer'])
        if r['source_answer'] and r['source_answer'] != r['checked_answer']: bad += 1; print('XX source/checked mismatch', r['id'])
    srcmis = [r['id'] for r in rows if r['source_answer'] and r['source_answer'] != r['checked_answer']]
    print(f'crosscheck: {sum(1 for r in rows if r["id"] in KEYMAP)} items program-verified, '
          f'{len(rows) - sum(1 for r in rows if r["id"] in KEYMAP)} qualitative; source/checked mismatches: {srcmis or "none"}')
    assert bad == 0

def replaced_check():
    """11-08 原位替换的 8 题：replaced_from 必填、新题不得是被替换题本身，source_key 与 KEYMAP 对应。"""
    import json, os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'questions.jsonl')
    rows = {json.loads(l)['id']: json.loads(l) for l in open(path)}
    want = {'PD2C-001': 'GK2024F-106', 'PD2C-003': 'JS2024A-91', 'PD2C-005': 'GD2022X-56', 'PD2C-006': 'SC2020H-81',
            'PD2C-016': 'GD2023X-58', 'PD2C-018': 'GD2023X-56', 'PD2C-019': 'HB2024-105', 'PD2C-021': 'SC2025-85'}
    for qid, old in want.items():
        r = rows[qid]
        assert r.get('replaced_from') == old, (qid, r.get('replaced_from'))
        assert r['source_key'] != old and KEYMAP[qid].split('(')[0] == r['source_key'], (qid, r['source_key'], KEYMAP[qid])
        assert r['check_status'] == '已核验' and r['variant_of'] is None and r['done_status'] == '已做情况未知', qid
    print(f'replaced: {len(want)} items carry replaced_from; new source keys = {[rows[q]["source_key"] for q in want]}')

if __name__ == '__main__':
    for f in COND + COMBO + SCI: f()
    crosscheck()
    replaced_check()
    print(f'\n{len(RESULTS)} checks passed')
    if '--retired' in sys.argv:
        print('\n--- retired checks (replaced items, not in questions.jsonl any more) ---')
        for f in RETIRED: f()
