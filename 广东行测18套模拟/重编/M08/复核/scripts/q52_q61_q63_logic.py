"""第52、63题 翻译推理：把题干写成条件命题，真值表全枚举检验各选项是否被蕴涵。
第61题：把题干与各选项的论证形式写成命题公式，检验是否有效（题干为肯后推前，无效）。"""
from itertools import product

def entails(varnames, premises, concl):
    for vals in product([False, True], repeat=len(varnames)):
        e = dict(zip(varnames, vals))
        if all(p(e) for p in premises) and not concl(e):
            return False
    return True
imp = lambda a, b: (not a) or b

print('== 第52题')
V = ['强国', '自强', '融合', '机遇', '优势', '文章']
prem = [lambda e: imp(e['强国'], e['自强']),      # 建设强国，关键在于科技自立自强
        lambda e: imp(e['机遇'], e['融合'])]      # 不断强化融合，才能抓住机遇
opts = {
 'A 融合→优势': lambda e: imp(e['融合'], e['优势']),
 'B 优势→文章': lambda e: imp(e['优势'], e['文章']),
 'C 非自强→非强国': lambda e: imp(not e['自强'], not e['强国']),
 'D 非机遇→非融合': lambda e: imp(not e['机遇'], not e['融合']),
}
for k, f in opts.items():
    print(k, '可推出' if entails(V, prem, f) else '推不出')

print('== 第63题（“稳住了企业，就业才有支撑”按“只有…才…”：就业→稳企）')
V = ['稳企', '就业', '民生', '显效', '余力', '运行']
prem = [lambda e: imp(e['就业'], e['稳企']), lambda e: imp(e['民生'], e['稳企']),
        lambda e: imp(e['余力'], e['显效']),          # 只有显效，小微才有余力
        lambda e: imp(e['运行'], e['余力'])]          # 除非余力，否则不能运行
opts = {
 'A 运行→显效': lambda e: imp(e['运行'], e['显效']),
 'B 稳企→(就业∨民生)': lambda e: imp(e['稳企'], e['就业'] or e['民生']),
 'C 显效→余力': lambda e: imp(e['显效'], e['余力']),
 'D 非民生→非就业': lambda e: imp(not e['民生'], not e['就业']),
}
for k, f in opts.items():
    print(k, '可推出' if entails(V, prem, f) else '推不出')
print('-- 若把首句误读为充分条件(稳企→就业∧民生)：')
prem2 = [lambda e: imp(e['稳企'], e['就业'] and e['民生'])] + prem[2:]
for k, f in opts.items():
    print(k, '可推出' if entails(V, prem2, f) else '推不出')

print('== 第61题 论证形式有效性')
forms = {
 '题干 P→Q, Q ∴ P': (['P', 'Q'], [lambda e: imp(e['P'], e['Q']), lambda e: e['Q']], lambda e: e['P']),
 'A 到期→申请, 非申请 ∴ 非到期': (['P', 'Q'], [lambda e: imp(e['P'], e['Q']), lambda e: not e['Q']], lambda e: not e['P']),
 'B 不标注→不端, 不标注 ∴ 不端': (['P', 'Q'], [lambda e: imp(e['P'], e['Q']), lambda e: e['P']], lambda e: e['Q']),
 'C 贮存→查验, 贮存 ∴ 查验': (['P', 'Q'], [lambda e: imp(e['P'], e['Q']), lambda e: e['P']], lambda e: e['Q']),
 'D 批发→制度, 制度 ∴ 批发': (['P', 'Q'], [lambda e: imp(e['P'], e['Q']), lambda e: e['Q']], lambda e: e['P']),
}
for k, (v, p, c) in forms.items():
    print(k, '有效' if entails(v, p, c) else '无效(肯后推前)')
