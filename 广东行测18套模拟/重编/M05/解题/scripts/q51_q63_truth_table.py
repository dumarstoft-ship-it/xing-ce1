"""Q51、Q63 翻译推理：真值表穷举，检验各选项是否在所有满足题干的赋值下都成立。"""
from itertools import product


def check(premises, options, names):
    worlds = [dict(zip(names, v)) for v in product([True, False], repeat=len(names))]
    ok = [w for w in worlds if all(p(w) for p in premises)]
    for k, f in options.items():
        print('  option %s: %s' % (k, 'ENTAILED (一定为真)' if all(f(w) for w in ok) else 'not entailed'))


imp = lambda p, q: (not p) or q

print('Q51')
# U=推动现代化产业体系整体升级, T=优化提升传统产业, J=技术改造, M=模式创新, S=结构优化, Z=迈向智能化, X=锻造新优势
names = ['U', 'T', 'J', 'M', 'S', 'Z', 'X']
premises = [
    lambda w: imp(w['U'], w['T']),                                  # 优化提升传统产业是整体升级的必然选择（必要条件）
    lambda w: imp(w['T'], w['J'] and w['M'] and w['S']),             # 只有技改、模式创新与结构优化，才能优化提升传统产业
    lambda w: imp(w['Z'] or w['X'], w['U']),                         # 智能化或锻造新优势 → 整体升级
]
options = {
    'A': lambda w: imp(not w['X'], not w['T']),
    'B': lambda w: imp(w['X'], w['J'] and w['M']),
    'C': lambda w: imp(w['J'] and w['M'] and w['S'], w['U']),        # 除非U，否则非(JMS) = (JMS)→U
    'D': lambda w: imp(w['T'], w['U']),
}
check(premises, options, names)

print('Q63')
# L=监管滞后, K=无人机可能沦为凶器, N=织密法治之网, F=科技创新真正造福人类
names = ['L', 'K', 'N', 'F']
premises = [lambda w: imp(w['L'], w['K']), lambda w: imp(w['F'], w['N'])]
options = {
    'A': lambda w: imp(not w['N'], not w['F']),
    'B': lambda w: imp(w['N'], w['F']),
    'C': lambda w: imp(not w['L'], not w['K']),
    'D': lambda w: imp(not w['K'], w['N']),
}
check(premises, options, names)
