"""第63题：对 Y(坚持原理)、G(把握规律)、S(抓住时机顺势而为)、W(无往不胜)、R(解决地位作用问题) 真值表穷举，
检验各选项是否被题干蕴涵。
第64题：用有限集合模型穷举检验各选项推理形式与题干是否一致、是否有效（“许多”按“有的”处理）。"""
import itertools

# ---------- 第63题 ----------
# 题干的推理关系只有三条：Y→G，G→S，W→S（“只有S，才W”）。首句是背景陈述，不构成条件关系。
def premises(Y, G, S, W, R):
    return ((not Y) or G) and ((not G) or S) and ((not W) or S)
opts63 = {
    'A': lambda Y, G, S, W, R: S or (not Y),          # ¬S → ¬Y
    'B': lambda Y, G, S, W, R: Y or (not G),          # ¬Y → ¬G
    'C': lambda Y, G, S, W, R: (not W) or Y,          # W → Y
    'D': lambda Y, G, S, W, R: (not G) or R,          # G → R（R：解决了人民群众地位和作用问题）
}
print('第63题')
for k, f in opts63.items():
    bad = [v for v in itertools.product([True, False], repeat=5) if premises(*v) and not f(*v)]
    print(' ', k, '必然成立' if not bad else f'不必然，反例(Y,G,S,W,R)={bad[0]}')

# ---------- 第64题 ----------
# 在含3个个体的论域上穷举三个集合，检验“前提真而结论假”的反例是否存在
U = range(3)
subsets = [frozenset(s) for r in range(4) for s in itertools.combinations(U, r)]
some = lambda A, B: len(A & B) > 0
allp = lambda A, B: A <= B
none_ = lambda A, B: len(A & B) == 0
forms = {
    '题干 有的A是B，所有B是C⇒有的A是C': (lambda A, B, C: some(A, B) and allp(B, C), lambda A, B, C: some(A, C)),
    'A项 所有A是B，有的A是C⇒所有B是C': (lambda A, B, C: allp(A, B) and some(A, C), lambda A, B, C: allp(B, C)),
    'B项 有的A是B，有的A是C⇒有的C是B': (lambda A, B, C: some(A, B) and some(A, C), lambda A, B, C: some(C, B)),
    'C项 有的A是B，所有B是C⇒有的A是C': (lambda A, B, C: some(A, B) and allp(B, C), lambda A, B, C: some(A, C)),
    'D项 有的A是B，所有B不是C⇒有的A是C': (lambda A, B, C: some(A, B) and none_(B, C), lambda A, B, C: some(A, C)),
}
print('第64题')
for name, (pre, con) in forms.items():
    cex = [(A, B, C) for A in subsets for B in subsets for C in subsets if pre(A, B, C) and not con(A, B, C)]
    print(' ', name, '：有效' if not cex else f'：无效，反例 A={set(cex[0][0])},B={set(cex[0][1])},C={set(cex[0][2])}')
