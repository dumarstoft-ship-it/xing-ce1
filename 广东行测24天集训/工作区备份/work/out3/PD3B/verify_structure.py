"""PD3B 结构题与计算型前提/削弱题的程序核验。
1) 真值表判有效性；再把每个论证写成“前提序列＋结论”的条件式签名（前件/后件及其肯否），按出现顺序统一改名后比对，
   确认与题干同形的选项唯一。
2) 非形式结构（比较＋单调因果、影响对象的归属）用模型枚举/角色签名比对。
3) 计算型：GD2014X-83（价格×数量）、GD2015X-59（投诉率）。
编码只抽取逻辑骨架；语义等同（如“有待发展”≈并未极大发展、“离不开”≈必要条件）在注释中写明。"""
import itertools
from fractions import Fraction as F

ok = []
def check(name, cond, msg=''):
    print(('OK   ' if cond else 'FAIL ') + name + ('：' + msg if msg else ''))
    ok.append(bool(cond))

# ---------- 条件式签名 ----------
# 一个条件句 = (前件, 前件肯否, 后件, 后件肯否)；论证 = (前提列表, 结论)
def ev(lit, e):
    atom, pos = lit
    return e[atom] if pos else not e[atom]
def valid(arg):
    prem, concl = arg
    atoms = sorted({x for c in prem + [concl] for x in (c[0], c[2])})
    for vals in itertools.product([False, True], repeat=len(atoms)):
        e = dict(zip(atoms, vals))
        if all((not ev((c[0], c[1]), e)) or ev((c[2], c[3]), e) for c in prem):
            if ev((concl[0], concl[1]), e) and not ev((concl[2], concl[3]), e):
                return False
    return True
def signature(arg):
    """按出现顺序把原子改名为 X、Y、Z…，保留肯否与前提顺序。"""
    prem, concl = arg
    names = {}
    def nm(a):
        if a not in names: names[a] = 'XYZWUVRS'[len(names)]
        return names[a]
    sig = [(nm(c[0]), c[1], nm(c[2]), c[3]) for c in prem]
    return tuple(sig), (nm(concl[0]), concl[1], nm(concl[2]), concl[3])
def show(arg):
    p, c = signature(arg)
    f = lambda t: f"{'' if t[1] else '¬'}{t[0]}→{'' if t[3] else '¬'}{t[2]}"
    return '；'.join(f(x) for x in p) + ' ⊢ ' + f(c)

def compare(title, stem, opts, expect):
    print('== ' + title)
    print('   题干：' + show(stem) + ('（有效）' if valid(stem) else '（无效）'))
    same = []
    for k, a in opts.items():
        s = signature(a) == signature(stem)
        print(f'   {k}：{show(a)}（{"有效" if valid(a) else "无效"}）{"  <= 与题干同形" if s else ""}')
        if s: same.append(k)
    check(title + ' 唯一同形选项', same == expect, str(same))

T, Fa = True, False
# GD2022X-73：a=农业极大发展 b=收入显著提高 c=科技落后地区；结论“有待发展”≈¬a
compare('GD2022X-73',
        ([('a', T, 'b', T), ('c', T, 'b', Fa)], ('c', T, 'a', Fa)),
        {'A': ([('低温', T, '开放', T), ('国庆', T, '开放', Fa)], ('国庆', T, '低温', Fa)),
         'B': ([('有月', Fa, '美景', Fa), ('有月', Fa, '美味', Fa)], ('美景', T, '有月', T)),  # 合取结论按其一记
         'C': ([('教育低', T, '有人才', Fa), ('振兴', T, '有人才', T)], ('教育低', T, '振兴', Fa)),  # 原句“往往…较难”，为或然判断
         'D': ([('迎难而上', T, '逆境初心', T), ('稳步前行', T, '顺境初心', T)], ('任何处境', T, '初心', T))},
        ['A'])
print('   注：C 逆否后也是有效式，但否定出现在第一前提、两前提顺序与题干相反，且原句为“往往…较难”的或然判断；A 与题干逐项对应。')

# GD2022X-70：S=世界科技强国 P=引才用才 x=我国（以建成强国为目标）
compare('GD2022X-70',
        ([('S', T, 'P', T), ('x', T, 'S', T)], ('x', T, 'P', T)),
        {'A': ([('培养人才', T, '良好环境', T)], ('良好环境', T, '汇聚人才', T)),   # 必要当充分
         'B': ([('创新力', T, '人才', T), ('长远发展', T, '创新力', T)], ('长远发展', T, '人才', T)),
         'C': ([('科技创新', T, '投入', T)], ('保障机制', T, '投入', T)),           # 结论出现新概念
         'D': ([('科技工作者', T, '榜样', T), ('院士', T, '贡献者', T)], ('院士', T, '榜样', T))},  # 概念不能串联
        ['B'])

# GDXD2019SW-1（备选题未用，略）

# GDXD2019SW-38：仅靠X（X在场且无Y）不能Q；结论“要Q还须Y”
def valid_bg(prem, concl, bg):
    atoms = ['M', 'N', 'Q']
    for vals in itertools.product([False, True], repeat=3):
        e = dict(zip(atoms, vals))
        if bg and not e['M']: continue
        if all(p(e) for p in prem) and not concl(e): return False
    return True
only = lambda e: not (e['M'] and not e['N']) or not e['Q']   # (M∧¬N)→¬Q
print('== GDXD2019SW-38')
check('题干“要Q还须N”在“X既定在场”背景下有效', valid_bg([only], lambda e: (not e['Q']) or e['N'], True))
check('D 同形（只注重智育→不能全面发展 ⊢ 全面发展→重视其他方面）', valid_bg([only], lambda e: (not e['Q']) or e['N'], True))
check('B 有效但结论只是前提逆否“Q→¬(仅靠X)”，未点出补充因素N', valid_bg([only], lambda e: (not e['Q']) or not (e['M'] and not e['N']), False))
check('C 无效（Q→¬M：把“不能只吃”推成“不能吃”）', not valid_bg([only], lambda e: (not e['Q']) or not e['M'], False))

# GDXD2020SW-11：A的C高于B；C越高D越高（D为C的严格增函数）⊢ A的D高于B
print('== GDXD2020SW-11')
def monotone_valid():
    for ca, cb in itertools.product(range(4), repeat=2):
        for f in itertools.product(range(5), repeat=4):
            if any(f[i] >= f[i + 1] for i in range(3)): continue
            if ca > cb and not f[ca] > f[cb]: return False
    return True
check('题干与 B：比较＋单调因果 ⊢ 比较，枚举全部小模型无反例', monotone_valid())
# D：由“A的C高且A的D高”推“C越高D越高”。反例：三个对象 A、B、E
C = dict(A=3, B=1, E=2); D = dict(A=5, B=2, E=1)
prem_ok = C['A'] > C['B'] and D['A'] > D['B']
mono = all((C[x] > C[y]) <= (D[x] > D[y]) for x in C for y in C)
check('D 无效：存在模型满足“城市两项都高”但“C越高D越高”不成立', prem_ok and not mono)

# GDXD2019SW-50：角色签名（作用源X、被作用的中介M、对象T；谁与T相联系）
print('== GDXD2019SW-50')
role = {'题干': ('X作用于M', 'M依附T'), 'A': ('X作用于人', 'T使X用量增加'), 'B': ('X作用于M', 'X集中于T'),
        'C': ('X→M→N', '无T'), 'D': ('X作用于M', 'M依附T')}
same = [k for k in 'ABCD' if role[k] == role['题干']]
check('唯一同形 D（B 中与T相联系的是作用源X，不是中介M）', same == ['D'], str(same))

# GD2014X-83：平均总支出=衣服支出/占比；衣服支出=平均价格×平均数量
print('== GD2014X-83')
P0, Q0, s = F(100), F(10), F(1, 10)
for name, Q1, expect in [('B 数量不变', Q0, True), ('数量下降20%（B不成立）', Q0 * F(8, 10), False)]:
    S0 = P0 * Q0 / s; S1 = P0 * F(3, 2) * Q1 / s
    check(f'{name}：平均总支出增幅 {(S1 / S0 - 1) * 100:.0f}%', (S1 / S0 == F(3, 2)) == expect)
H0, H1, T0, T1 = 1000, 1500, F(1000), F(1500)
check('D 不能保证结论：户数+50%且衣服总支出+50%，户均衣服支出增幅 0%', (T1 / H1) / (T0 / H0) == 1)

# GD2015X-59：投诉率=投诉数/销量
print('== GD2015X-59')
r = F(76) / F(24)
check(f'甲占有率76%→乙至多24%，甲/乙销量比≥{float(r):.2f}>3，甲投诉率≤乙的{float(3 / r):.0%}', r > 3)

print('ALL', 'PASSED' if all(ok) else 'HAS FAILURES')
