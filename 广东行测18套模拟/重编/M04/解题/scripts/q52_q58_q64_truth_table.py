# -*- coding: utf-8 -*-
"""Q52 真假推理、Q58 翻译推理、Q53 搭桥、Q64 结构比较 的真值表核验。"""
import itertools

imp = lambda a, b: (not a) or b

print('== Q52：甲乙丙三个品牌，中标情况任意（可多个中标），三人中只有一人说对')
sols = []
for j, y, b in itertools.product([True, False], repeat=3):   # 甲 乙 丙 是否中标
    s1 = j and y                 # 小李：甲、乙均中标
    s2 = imp(b, j)               # 小张：若丙中标则甲中标
    s3 = not (j and y)           # 小王：甲乙至多一个中标
    if [s1, s2, s3].count(True) == 1:
        sols.append((j, y, b))
for s in sols:
    print('   甲%s 乙%s 丙%s' % tuple('中' if v else '未' for v in s))
opts = {'A 甲、乙均中标': lambda j, y, b: j and y, 'B 乙、丙均中标': lambda j, y, b: y and b,
        'D 只有丙中标': lambda j, y, b: b and not j and not y}
for k, f in opts.items():
    print('  ', k, '必然成立' if all(f(*s) for s in sols) else '不必然成立')
print('   C 乙可能中标：', '成立（存在乙中标的情形）' if any(s[1] for s in sols) else '不成立',
      '；且乙也可能不中标' if any(not s[1] for s in sols) else '')

print('== Q58：E=营造良好教育生态，X1/X2/X3=三项措施，C=为超前学习降温')
print('   题干：E→(X1∧X2∧X3)（唯有如此方能E），C→E（只有E才能C）')
names = ['X1', 'X2', 'X3', 'E', 'C']
worlds = [dict(zip(names, v)) for v in itertools.product([True, False], repeat=5)]
worlds = [w for w in worlds if imp(w['E'], w['X1'] and w['X2'] and w['X3']) and imp(w['C'], w['E'])]
checks = {
    'A ¬X1→¬X3': lambda w: imp(not w['X1'], not w['X3']),
    'B ¬E→¬X2': lambda w: imp(not w['E'], not w['X2']),
    'C X1→C': lambda w: imp(w['X1'], w['C']),
    'D ¬X3→¬C': lambda w: imp(not w['X3'], not w['C']),
}
for k, f in checks.items():
    print('  ', k, '必然为真' if all(f(w) for w in worlds) else '不必然为真')

print('== Q53：题干 懂艺术→懂书法，结论 理解美学→懂书法；检验各项补上后能否推出结论')
names = ['art', 'cal', 'aes', 'enjoy']
base = lambda w: imp(w['art'], w['cal'])
concl = lambda w: imp(w['aes'], w['cal'])
adds = {
    'C 理解美学→懂艺术（“基本途径”按必要条件理解）': lambda w: imp(w['aes'], w['art']),
    'D 欣赏书法→理解美学': lambda w: imp(w['enjoy'], w['aes']),
}
for k, f in adds.items():
    ws = [dict(zip(names, v)) for v in itertools.product([True, False], repeat=4)]
    ok = all(concl(w) for w in ws if base(w) and f(w))
    print('  ', k, '：补上后结论', '必然成立' if ok else '不必然成立')

print('== Q64：比较各项的推理形式（A→E、B→E ∴ E→A∨B 型）')


def form_signature(premises, conclusion, nvar):
    """返回 (前提能否推出结论)，并打印形式"""
    ws = list(itertools.product([True, False], repeat=nvar))
    return all(conclusion(*w) for w in ws if all(p(*w) for p in premises))


forms = {
    '题干：A→E，B→E ∴ E→(A∨B)': ([lambda a, b, e: imp(a, e), lambda a, b, e: imp(b, e)], lambda a, b, e: imp(e, a or b)),
    'D：A→E，B→E ∴ E→(A∨B)': ([lambda a, b, e: imp(a, e), lambda a, b, e: imp(b, e)], lambda a, b, e: imp(e, a or b)),
    'A：X→Y，X→Z ∴ X→(Y∨Z)': ([lambda x, y, z: imp(x, y), lambda x, y, z: imp(x, z)], lambda x, y, z: imp(x, y or z)),
    'B：P→G，R→G ∴ (P∨R)→G': ([lambda p, r, g: imp(p, g), lambda p, r, g: imp(r, g)], lambda p, r, g: imp(p or r, g)),
}
for k, (ps, c) in forms.items():
    print('  ', k, '（前提能否推出结论：%s）' % form_signature(ps, c, 3))
print('   C：F→M，S→O ∴ (F∨S)→O（两个前提的后件不同，结构不同）')
