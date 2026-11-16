# 第57、63、64题：用真值表检验各选项能否由题干推出（或推理形式是否有效）
import itertools
imp = lambda p, q: (not p) or q

def entails(premises, conclusion, n):
    for v in itertools.product((False, True), repeat=n):
        if all(p(*v) for p in premises) and not conclusion(*v):
            return False
    return True

print('== 第57题 ==')
# 变量：Z中国式现代化 N农业农村现代化 G尊重规律 S实事求是 W行稳致远 Y因地制宜 J精准施策 F筑牢防返贫底线 H建设和美乡村
P57 = [lambda Z, N, G, S, W, Y, J, F, H: imp(Z, N),               # 中国式现代化离不开农业农村现代化
       lambda Z, N, G, S, W, Y, J, F, H: imp(W, G and S),         # 尊重规律、实事求是才能行稳致远
       lambda Z, N, G, S, W, Y, J, F, H: imp(Y and J, F)]         # 坚守因地制宜、秉持精准施策就能筑牢底线
O57 = {'A 只要因地制宜就能筑牢防返贫底线': lambda Z, N, G, S, W, Y, J, F, H: imp(Y, F),
       'B 不能实事求是就无法行稳致远': lambda Z, N, G, S, W, Y, J, F, H: imp(not S, not W),
       'C 中国式现代化是农业农村现代化的必要条件': lambda Z, N, G, S, W, Y, J, F, H: imp(N, Z),
       'D 只有因地制宜、精准施策才能建设和美乡村': lambda Z, N, G, S, W, Y, J, F, H: imp(H, Y and J)}
for k, c in O57.items():
    print(f'  {k}: {"能推出" if entails(P57, c, 9) else "推不出"}')

print('== 第63题 ==')
# P持续深化整治形式主义为基层减负 Q有更多时间精力干实事 R杜绝形象工程政绩工程 S真正满足群众需求
P63 = [lambda P, Q, R, S: imp(P, Q), lambda P, Q, R, S: imp(not P, not R), lambda P, Q, R, S: imp(S, R)]
O63 = {'A S→Q': lambda P, Q, R, S: imp(S, Q), 'B Q→R': lambda P, Q, R, S: imp(Q, R),
       'C ¬S→¬P': lambda P, Q, R, S: imp(not S, not P), 'D P→R': lambda P, Q, R, S: imp(P, R)}
for k, c in O63.items():
    print(f'  {k}: {"能推出" if entails(P63, c, 4) else "推不出"}')

print('== 第64题（各段推理的形式与有效性） ==')
# 统一记号：E 目标结果；A、B 第一句中的两个必要条件；C 第二句中 B 的必要条件
forms = {
  '题干': ('E→A∧B；B→C；所以 ¬C→¬E',
           [lambda E, A, B, C: imp(E, A and B), lambda E, A, B, C: imp(B, C)], lambda E, A, B, C: imp(not C, not E)),
  'A项': ('E→F(家庭与学校教育融合协同，一个整体条件)；B(学校教育)→C；所以 ¬C→¬E（F与B不是同一概念）',
           [lambda E, A, B, C: imp(E, A), lambda E, A, B, C: imp(B, C)], lambda E, A, B, C: imp(not C, not E)),
  'B项': ('E→B；¬C1∨¬C2→¬B 即 B→C1∧C2；所以 E→C2（结论“C2是E的前提”）',
           [lambda E, A, B, C: imp(E, B), lambda E, A, B, C: imp(B, A and C)], lambda E, A, B, C: imp(E, C)),
  'C项': ('E→A∧B；B→C；所以 ¬B→¬E（结论落在B而不是C上）',
           [lambda E, A, B, C: imp(E, A and B), lambda E, A, B, C: imp(B, C)], lambda E, A, B, C: imp(not B, not E)),
  'D项': ('E→A∧B；B→C；所以 ¬C→¬E',
           [lambda E, A, B, C: imp(E, A and B), lambda E, A, B, C: imp(B, C)], lambda E, A, B, C: imp(not C, not E)),
}
for k, (desc, prem, concl) in forms.items():
    print(f'  {k}: {desc}  —— 形式{"有效" if entails(prem, concl, 4) else "无效"}')
