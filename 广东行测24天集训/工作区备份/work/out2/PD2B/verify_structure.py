"""PD2B 结构题程序核验：把题干与选项编码成命题形式，用真值表判有效性，并按"推理形式"匹配，确认唯一答案。
编码只抽取逻辑骨架（条件方向、小前提肯/否哪一件、结论），语义等同（如“并不认可低碳出行”≈“不践行”）由编者在注释中写明。"""
import itertools

def valid(premises, conclusion, atoms):
    for vals in itertools.product([False, True], repeat=len(atoms)):
        env = dict(zip(atoms, vals))
        if all(p(env) for p in premises) and not conclusion(env):
            return False
    return True

def imp(a, b): return lambda e: (not e[a]) or e[b]
def lit(a, pos=True): return lambda e: e[a] if pos else not e[a]

def mp_form(cond, minor, concl):
    """cond=(X,Y) 表示 X→Y；minor/concl=(atom, 肯/否)。返回(形式名, 是否有效)"""
    X, Y = cond
    name = {(X, True): '肯前', (X, False): '否前', (Y, True): '肯后', (Y, False): '否后'}[minor]
    ok = valid([imp(X, Y), lit(*minor)], lit(*concl), [X, Y])
    return name, ok

def report(title, stem, opts):
    s = mp_form(*stem)
    print(f'== {title}: 题干 {s}')
    hits = []
    for k, v in opts.items():
        f = mp_form(*v) if v else ('其他', None)
        same = f == s
        hits += [k] if same else []
        print(f'   {k}: {f} {"<= 同形" if same else ""}')
    print('   唯一同形选项:', hits, 'OK' if len(hits) == 1 else 'NOT UNIQUE')
    return hits

# GD2023X-69 原题：只有P(不间断练习)才Q(获奖) => Q→P；小李¬Q；∴¬P
opts69 = {
    'A': (('Q', 'P'), ('Q', False), ('P', False)),   # 降成本(P)是利润上涨(Q)必要条件；利润没涨；∴没降成本
    'B': (('Q', 'P'), ('Q', True), ('P', True)),     # 除非能力过硬(P)否则无法成优秀(Q) => Q→P；小张Q；∴P
    'C': (('Q', 'P'), ('P', False), ('Q', False)),   # 要减排(Q)就要低碳出行(P)；不认可(≈不践行)P；∴无法减排
    'D': (('P', 'Q'), ('Q', False), ('P', False)),   # 价格大幅降(P)→销量迅速升(Q)；Q未发生；∴P未发生（原文另有“大幅”与“下降”的量词滑移）
}
a = report('GD2023X-69 原题', (('Q', 'P'), ('Q', False), ('P', False)), opts69)
b = report('PD2B改编（小前提改为“获奖了”，结论改为“一定不间断练习了”）', (('Q', 'P'), ('Q', True), ('P', True)), opts69)
assert a == ['A'] and b == ['B']

# GD2021Z-65（=GD2021X-65）：希望过好日子H→愿意辅导F；小王F；∴H（肯后）
report('GD2021Z-65', (('H', 'F'), ('F', True), ('H', True)), {
    'A': (('S', 'T'), ('T', True), ('S', True)),     # 出售S→通过检测T；苹果T；∴苹果S
    'B': None,                                         # 张家用了→好；李家不好→没用：两个主体的对照/类比，非同一条件句推理
    'C': None,                                         # 许多…许多…→都：归纳概括
    'D': (('Q', 'P'), ('P', False), ('Q', False)),   # 只有经Ⅲ期P才可能上市Q => Q→P；没经P；∴未上市
})

# 链式：GD2019X-60 题干 a→b→c，∴ c→a（把“能导致”倒成“想要就必须/都会”）
def chain_check():
    atoms = ['a', 'b', 'c']
    prem = [imp('a', 'b'), imp('b', 'c')]
    print('== GD2019X-60 链式：前提 a→b, b→c')
    print('   推出 a→c 有效?', valid(prem, imp('a', 'c'), atoms), '（A项“充分条件”方向）')
    print('   推出 c→a 有效?', valid(prem, imp('c', 'a'), atoms), '（题干与D项的倒置方向）')
    print('   B项结论 b→a（倒置第一环）有效?', valid(prem, imp('b', 'a'), atoms))
    # SD2024-95：繁荣a→科技b，科技b→人才c，∴ a→c；D同；B结论 a→b 只是复述前提
    print('== SD2024-95 链式：a→b, b→c ∴ a→c 有效?', valid(prem, imp('a', 'c'), atoms),
          '；B项结论“急需产业振兴”= a→b，为复述第一前提，结论项不同')
chain_check()
print('ALL CHECKS DONE')
