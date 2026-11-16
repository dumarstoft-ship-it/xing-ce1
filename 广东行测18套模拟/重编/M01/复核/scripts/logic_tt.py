"""第57、63、64题：真值表检验选项是否可由题干推出 / 结构是否同型。"""
import itertools


def imp(a, b):
    return (not a) or b


def entails(premises, concl, nvars):
    for v in itertools.product((False, True), repeat=nvars):
        if all(p(*v) for p in premises) and not concl(*v):
            return False
    return True


# ---- 第63题 ----
# P=持续深化整治形式主义为基层减负, Q=基层有更多时间精力干实事, R=杜绝形象/政绩工程, S=真正满足群众切实需求
prem63 = [lambda P, Q, R, S: imp(P, Q),
          lambda P, Q, R, S: imp(not P, not R),
          lambda P, Q, R, S: imp(S, R)]
opt63 = {
    "A S->Q": lambda P, Q, R, S: imp(S, Q),
    "B Q->R": lambda P, Q, R, S: imp(Q, R),
    "C ~S->~P": lambda P, Q, R, S: imp(not S, not P),
    "D P->R": lambda P, Q, R, S: imp(P, R),
}
print("第63题")
for k, f in opt63.items():
    print("  ", k, "可推出" if entails(prem63, f, 4) else "推不出")

# ---- 第57题 ----
# Y=因地制宜, J=精准施策, F=筑牢防返贫底线, G=尊重规律, T=实事求是, X=行稳致远, Z=中国式现代化, N=农业农村现代化, M=和美乡村
names = "Y J F G T X Z N M".split()
prem57 = [
    lambda Y, J, F, G, T, X, Z, N, M: imp(Z, N),            # 中国式现代化离不开农业农村现代化
    lambda Y, J, F, G, T, X, Z, N, M: imp(X, G and T),      # 尊重规律、实事求是才能行稳致远
    lambda Y, J, F, G, T, X, Z, N, M: imp(Y and J, F),      # 坚守因地制宜、秉持精准施策，就能筑牢底线
]
opt57 = {
    "A Y->F": lambda Y, J, F, G, T, X, Z, N, M: imp(Y, F),
    "B ~T->~X": lambda Y, J, F, G, T, X, Z, N, M: imp(not T, not X),
    "C N->Z (Z是N的必要条件)": lambda Y, J, F, G, T, X, Z, N, M: imp(N, Z),
    "D M->(Y且J)": lambda Y, J, F, G, T, X, Z, N, M: imp(M, Y and J),
}
print("第57题")
for k, f in opt57.items():
    print("  ", k, "可推出" if entails(prem57, f, 9) else "推不出")

# ---- 第64题：抽象形式 ----
# 题干：C->(A且B)；B->D；结论 ~D->~C
print("第64题（形式比对）")
forms = {
    "题干": ("C->(A&B)", "B->D", "~D->~C"),
    "A": ("C->(A与B融合协同)", "B->D", "~D->~C  (前提中的必要条件是‘融合协同’整体, 与B不同项)"),
    "B": ("C->B", "B->(X&Y)  [~X或~Y -> ~B]", "C->Y   (合取在第二个前提，结论是必要条件)"),
    "C": ("C->(A&B)", "B->D", "~B->~C (结论没用到D)"),
    "D": ("C->(A&B)", "B->D", "~D->~C"),
}
for k, v in forms.items():
    print("  ", k, v)
# 验证题干与D形式有效
valid = entails([lambda A, B, C, D: imp(C, A and B), lambda A, B, C, D: imp(B, D)],
                lambda A, B, C, D: imp(not D, not C), 4)
print("   题干/D 形式有效:", valid)
