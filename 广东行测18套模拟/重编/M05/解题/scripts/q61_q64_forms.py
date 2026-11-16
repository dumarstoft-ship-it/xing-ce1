"""Q61、Q64 结构比较：把题干和各选项写成形式（前提 ⊢ 结论），比较形式是否相同，并用真值表判断是否有效。"""
from itertools import product

imp = lambda p, q: (not p) or q


def valid(premises, concl, n=3):
    for v in product([True, False], repeat=n):
        if all(p(*v) for p in premises) and not concl(*v):
            return False
    return True


print('Q61  形式: P→Q, Q ⊢ P（肯定后件，无效）')
forms61 = {
    '题干 若非A则非B; A ⊢ B  (等价 B→A, A ⊢ B)': ([lambda a, b, c: imp(not a, not b), lambda a, b, c: a], lambda a, b, c: b),
    'A 若P则Q; P ⊢ Q': ([lambda a, b, c: imp(a, b), lambda a, b, c: a], lambda a, b, c: b),
    'B 除非P否则非Q; Q ⊢ P  (Q→P, Q ⊢ P)': ([lambda a, b, c: imp(not a, not b), lambda a, b, c: b], lambda a, b, c: a),
    'C 只有P才Q; P ⊢ 非Q': ([lambda a, b, c: imp(b, a), lambda a, b, c: a], lambda a, b, c: not b),
    'D 若P则Q; Q ⊢ P': ([lambda a, b, c: imp(a, b), lambda a, b, c: b], lambda a, b, c: a),
}
for k, (pr, c) in forms61.items():
    print('  %-40s 有效=%s' % (k, valid(pr, c)))

print('Q64  形式: A→B, B→C ⊢ A→C（有效）')
forms64 = {
    '题干 明厨亮灶→客流大, 客流大→美味 ⊢ 明厨亮灶→美味': ([lambda a, b, c: imp(a, b), lambda a, b, c: imp(b, c)], lambda a, b, c: imp(a, c)),
    'A 晨读→语感, 语感→效率高 ⊢ 效率高→晨读': ([lambda a, b, c: imp(a, b), lambda a, b, c: imp(b, c)], lambda a, b, c: imp(c, a)),
    'B 重视质量→口碑好, 口碑好→占有率高 ⊢ 重视质量→占有率高': ([lambda a, b, c: imp(a, b), lambda a, b, c: imp(b, c)], lambda a, b, c: imp(a, c)),
    'C 作息规律→代谢稳, 代谢稳→衰老慢 ⊢ 非作息规律→非衰老慢': ([lambda a, b, c: imp(a, b), lambda a, b, c: imp(b, c)], lambda a, b, c: imp(not a, not c)),
    'D 垃圾分类→整洁, 整洁→幸福感强 ⊢ 幸福感强→垃圾分类': ([lambda a, b, c: imp(a, b), lambda a, b, c: imp(b, c)], lambda a, b, c: imp(c, a)),
}
for k, (pr, c) in forms64.items():
    print('  %-50s 有效=%s' % (k, valid(pr, c)))


# Q61 形式归类：把条件句统一写成“原命题/逆否命题”等价类，看第二个前提肯定的是前件还是后件、结论落在哪一项
def classify(cond, fact, concl):
    """cond=(ante, cons)，文字用 ('X', True/False) 表示 X 或 非X。返回原命题与逆否命题两种读法下的形式集合。"""
    neg = lambda l: (l[0], not l[1])
    ante, cons = cond
    out = set()
    for a_, c_ in ((ante, cons), (neg(cons), neg(ante))):   # 原命题与逆否命题等价
        if fact == a_ and concl == c_:
            out.add('肯定前件')
        elif fact == c_ and concl == a_:
            out.add('肯定后件')
        elif fact == neg(a_) and concl == neg(c_):
            out.add('否定前件')
        elif fact == neg(c_) and concl == neg(a_):
            out.add('否定后件')
        else:
            out.add('其他')
    return '/'.join(sorted(out))


print('Q61 形式归类')
cases = {
    '题干': ((('A', False), ('B', False)), ('A', True), ('B', True)),
    'A': ((('P', True), ('Q', True)), ('P', True), ('Q', True)),
    'B': ((('P', False), ('Q', False)), ('Q', True), ('P', True)),
    'C': ((('Q', True), ('P', True)), ('P', True), ('Q', False)),
    'D': ((('P', True), ('Q', True)), ('Q', True), ('P', True)),
}
stem = classify(*cases['题干'])
for k, (cond, fact, concl) in cases.items():
    c = classify(cond, fact, concl)
    print('  %-4s %-12s 与题干同形=%s' % (k, c, c == stem))
