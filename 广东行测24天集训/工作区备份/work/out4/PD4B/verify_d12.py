# -*- coding: utf-8 -*-
"""PD4B D12 程序核验：结构题的形式比对（不使用前提先后顺序）、平均数前提、基数、区分度定义。
运行：python3 verify_d12.py   （同时与 questions.jsonl 的 checked_answer 逐题对照）
形式比对的规则：把每个论证写成（前提集合，结论）；两个论证“同形”当且仅当存在命题变元的一一改名，
使前提集合两两逻辑等价（不计顺序）、结论逻辑等价。只改名，不允许把某个变元换成它的否定——
所以“肯定/否定落在哪一端”会被区分；前提的先后顺序不参与判定。"""
import itertools, json, os, sys
from fractions import Fraction as F

def tt(f, atoms):
    return tuple(bool(f(dict(zip(atoms, vals)))) for vals in itertools.product([False, True], repeat=len(atoms)))
def imp(a, b): return (not a) or b
class Arg:
    def __init__(self, atoms, premises, concl, modal='确定', note=''):
        self.atoms, self.premises, self.concl, self.modal, self.note = atoms, premises, concl, modal, note
    def valid(self):
        for vals in itertools.product([False, True], repeat=len(self.atoms)):
            e = dict(zip(self.atoms, vals))
            if all(p(e) for p in self.premises) and not self.concl(e): return False
        return True
def same_form(x, y):
    if x is None or y is None: return False
    if len(x.atoms) != len(y.atoms) or len(x.premises) != len(y.premises): return False
    base = x.atoms
    tx_p = sorted(tt(p, base) for p in x.premises); tx_c = tt(x.concl, base)
    for perm in itertools.permutations(y.atoms):
        ren = dict(zip(base, perm))            # x 的变元 -> y 的变元
        def lift(g): return lambda e, g=g: g({ren[k]: e[k] for k in base})
        ty_p = sorted(tt(lift(p), base) for p in y.premises); ty_c = tt(lift(y.concl), base)
        if tx_p == ty_p and tx_c == ty_c: return True
    return False

RESULT = {}
def structure(key, stem, opts, expect):
    same = [k for k, a in opts.items() if same_form(stem, a)]
    print(f'[{key}] 题干：有效={stem.valid()}，{stem.modal}；{stem.note}')
    for k, a in opts.items():
        if a is None: print(f'   {k}: 非条件句推理（不参与比对）'); continue
        print(f'   {k}: 有效={a.valid()}，{a.modal}，与题干同形={same_form(stem, a)}；{a.note}')
    assert same == [expect], (key, same)
    print(f'   => 唯一同形项：{same[0]}（期望 {expect}）'); RESULT[key] = same[0]

# ---------- JS2018A-94：爱家乡→不说坏话；不说坏话；所以爱家乡 ----------
structure('JS2018A-94',
    Arg(['P', 'Q'], [lambda e: imp(e['P'], e['Q']), lambda e: e['Q']], lambda e: e['P'], note='P→Q，Q ⊢ P（肯定后件）'),
    {'A': Arg(['P', 'Q', 'R'], [lambda e: imp(not e['P'], e['Q']), lambda e: not e['Q']], lambda e: e['R'], note='非P→Q，非Q ⊢ R（结论是新项“话很重要”）'),
     'B': Arg(['P', 'Q'], [lambda e: imp(e['P'], e['Q']), lambda e: e['P']], lambda e: e['Q'], modal='或然（往往）', note='P→Q，P ⊢ Q（肯定前件）'),
     'C': Arg(['P', 'Q'], [lambda e: imp(e['P'], e['Q']), lambda e: not e['Q']], lambda e: not e['P'], note='P→Q，非Q ⊢ 非P（否定后件）'),
     'D': Arg(['P', 'Q'], [lambda e: imp(e['P'], e['Q']), lambda e: e['Q']], lambda e: e['P'], note='P→Q，Q ⊢ P（肯定后件）')}, 'D')

# ---------- GDXD2019SW-46：没解决安全问题→不能普及；所以解决了→普及 ----------
structure('GDXD2019SW-46',
    Arg(['P', 'Q'], [lambda e: imp(not e['P'], not e['Q'])], lambda e: imp(e['P'], e['Q']), note='非P→非Q ⊢ P→Q（否定前件／必要当充分）'),
    {'A': Arg(['P', 'Q'], [lambda e: imp(not e['P'], not e['Q']), lambda e: not e['Q']], lambda e: not e['P'], note='非P→非Q，非Q ⊢ 非P（肯定后件，多一个事实前提）'),
     'B': Arg(['P', 'Q'], [lambda e: imp(not e['P'], not e['Q'])], lambda e: imp(e['P'], e['Q']), note='非P→非Q ⊢ P→Q'),
     'C': Arg(['P', 'Q'], [lambda e: imp(e['P'], e['Q'])], lambda e: imp(not e['Q'], not e['P']), note='P→Q ⊢ 非Q→非P（逆否，有效）'),
     'D': None}, 'B')

# ---------- SC2022S-76：做好→党性原则；党性原则→党的领导；所以做好→党的领导 ----------
structure('SC2022S-76',
    Arg(['A', 'B', 'C'], [lambda e: imp(e['A'], e['B']), lambda e: imp(e['B'], e['C'])], lambda e: imp(e['A'], e['C']), note='A→B，B→C ⊢ A→C（连锁）'),
    {'A': Arg(['A', 'B', 'C'], [lambda e: e['A'], lambda e: e['B']], lambda e: e['C'], note='两个互不相接的陈述 ⊢ 新判断'),
     'B': Arg(['A', 'B', 'S', 'U'], [lambda e: imp(e['A'], e['B']), lambda e: e['S']], lambda e: e['U'], note='A→B，另一陈述S ⊢ U“刻不容缓”（结论不是由首尾两项组成的条件句）'),
     'C': Arg(['A', 'B', 'C'], [lambda e: imp(e['A'], e['B']), lambda e: imp(e['C'], e['B'])], lambda e: imp(e['A'], e['C']), note='A→B，C→B ⊢ A→C（共用后件，无效）'),
     'D': Arg(['A', 'B', 'C'], [lambda e: imp(e['A'], e['B']), lambda e: imp(e['B'], e['C'])], lambda e: imp(e['A'], e['C']), note='A→B，B→C ⊢ A→C')}, 'D')

# ---------- 备选 GD2022X-75 的 D 项、GDXD 等不在此列；以下为数值类 ----------
def mean(xs): return F(sum(xs), len(xs))

# GDXD2020SW-27：天天公司 t 从 A 县搬到 B 县，两县平均都上升 => ②③必然成立；①④不必然
cnt = 0; viol2 = viol3 = 0; ex1 = ex4 = None
vals = range(1, 8)
for na in (2, 3):
    for nb in (2, 3):
        for A in itertools.combinations_with_replacement(vals, na):
            for B in itertools.combinations_with_replacement(vals, nb):
                for t in vals:
                    a_before, a_after = mean(list(A) + [t]), mean(A)
                    b_before, b_after = mean(B), mean(list(B) + [t])
                    if a_after > a_before and b_after > b_before:
                        cnt += 1
                        if not (t < a_before): viol2 += 1                 # ② 天天低于A县企业的平均
                        if not (b_before < a_before): viol3 += 1          # ③ B县平均低于A县
                        if ex1 is None and not all(t < x for x in A): ex1 = (A, B, t)   # ① 不成立的例子
                        pairs = [(b, a) for b in B for a in list(A) + [t]]
                        if ex4 is None and sum(b < a for b, a in pairs) * 2 < len(pairs): ex4 = (A, B, t)  # ④“普遍低于”不成立
assert cnt > 0 and viol2 == 0 and viol3 == 0 and ex1 and ex4
print(f'[GDXD2020SW-27] 两县平均都上升的情形 {cnt} 个：②不成立 {viol2} 个，③不成立 {viol3} 个；'
      f'①不成立的例子 A县其他企业={ex1[0]} B县={ex1[1]} 天天={ex1[2]}；④不成立的例子 A县其他企业={ex4[0]} B县={ex4[1]} 天天={ex4[2]}')
RESULT['GDXD2020SW-27'] = 'C'

# SD2023-69：不及格者中90%打游戏；若全体中打游戏者也占90%，两组不及格率相等
N, fail = 1000, 100
fail_play = fail * 90 // 100; play = N * 90 // 100
r1 = F(fail_play, play); r2 = F(fail - fail_play, N - play)
assert r1 == r2
print(f'[SD2023-69] 打游戏者不及格率={r1}，不打游戏者不及格率={r2}，相等 => 论据不支持“更容易导致”')
RESULT['SD2023-69'] = 'A'

# JS2024A-102：N=100，高分组、低分组各27人；h、l 为两组答对人数，m 为中间组答对人数
n, g = 100, 27
allD = {}
for h in range(g + 1):
    for l in range(g + 1):
        for m in range(n - 2 * g + 1):
            p = F(h + m + l, n); D = F(h, g) - F(l, g)
            allD.setdefault(p, set()).add(D)
A_ok = allD[F(1)] == {F(0)}                       # 难度1 => D 只能是0
B_neg = any(d < 0 for ds in allD.values() for d in ds)   # 存在负值
C_max = max(allD[F(27, 100)])                     # 难度0.27 的最大 D
assert A_ok and B_neg and C_max == 1
# D项：单选题得分只有 0 或满分 s；平均分/分值 = 答对比例
s = 2; k = 37
assert F(k * s, n) / s == F(k, n)
print(f'[JS2024A-102] A：难度1时D恒为0（非0.1）；B：存在D<0；C：难度0.27时D最大值={C_max}（非0.5）；D：平均分/分值=答对比例，恒等')
RESULT['JS2024A-102'] = 'D'

# ---------- 与 questions.jsonl 对照 ----------
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'questions.jsonl')
if os.path.exists(p):
    rows = {json.loads(l)['source_key']: json.loads(l) for l in open(p, encoding='utf-8')}
    for k, v in RESULT.items():
        assert rows[k]['checked_answer'] == v, (k, rows[k]['checked_answer'], v)
    print('与 questions.jsonl 的 checked_answer 对照：', len(RESULT), '题全部一致')
print('ALL OK')
