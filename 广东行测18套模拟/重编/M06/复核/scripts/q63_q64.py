"""第63题：真值表检验；第64题：用小集合模型检验各选项与题干推理结构是否一致（是否有效）。"""
import itertools

# ---- 第63题 ----
# P=坚持基本原理, Q=把握规律, R=抓住时机顺势而为, S=无往而不胜, M=解决了地位作用问题（题干首句，作为独立命题）
prem = lambda P, Q, R, S, M: (not P or Q) and (not Q or R) and (not S or R)
opts63 = {
    'A': lambda P, Q, R, S, M: R or not P,          # ¬R → ¬P
    'B': lambda P, Q, R, S, M: P or not Q,          # ¬P → ¬Q
    'C': lambda P, Q, R, S, M: not S or P,          # S → P
    'D': lambda P, Q, R, S, M: not Q or M,          # Q → M
}
print('第63题：')
for k, f in opts63.items():
    valid = all(f(*v) for v in itertools.product([True, False], repeat=5) if prem(*v))
    print(f'  选项{k} 由题干必然推出：{valid}')

# ---- 第64题 ----
# 在至多3个个体的论域上枚举谓词，检验"前提真而结论假"的反例是否存在。
# "许多X是Y"按"有的X是Y"处理（逻辑上同为特称）。
U = range(3)
subsets = [frozenset(s) for r in range(4) for s in itertools.combinations(U, r)]
some = lambda X, Y: len(X & Y) > 0
allp = lambda X, Y: X <= Y
none_ = lambda X, Y: not (X & Y)


def valid(f):
    for A, B, C in itertools.product(subsets, repeat=3):
        prem, concl = f(A, B, C)
        if prem and not concl:
            return False
    return True


forms = {
    '题干 许多A是B，所有B是C → 许多A是C': lambda A, B, C: (some(A, B) and allp(B, C), some(A, C)),
    'A 所有A是B，有的A是C → 所有B是C': lambda A, B, C: (allp(A, B) and some(A, C), allp(B, C)),
    'B 许多A是B，许多A是C → 许多C是B': lambda A, B, C: (some(A, B) and some(A, C), some(C, B)),
    'C 许多A是B，所有B是C → 许多A是C': lambda A, B, C: (some(A, B) and allp(B, C), some(A, C)),
    'D 有些A是B，所有B都不是C → 有些A是C': lambda A, B, C: (some(A, B) and none_(B, C), some(A, C)),
}
print('第64题（结构 / 是否有效）：')
for k, f in forms.items():
    print(f'  {k}：有效={valid(f)}')
