"""第56题：4人4门课。每人主导1门（主导为一一对应），并检查另一门（不能检查自己主导的那门）。
在"违背条件(4)"即"小喜检查古代 且 安安主导外国"的前提下，枚举满足(1)(2)(3)的安排，检验各选项。
同时检验两种理解：检查也一一对应 / 检查不要求一一对应。"""
import itertools

P = ['小平', '安安', '小喜', '乐乐']
C = ['古代', '外国', '现代', '概论']


def conds(lead, chk):
    c1 = not (lead['小平'] == '古代') or chk['小喜'] == '外国'
    c2 = not (lead['安安'] == '外国') or chk['乐乐'] == '概论'
    c3 = not (lead['小喜'] == '概论') or lead['乐乐'] == '外国'
    c4 = not (chk['小喜'] == '古代') or lead['安安'] != '外国'
    return c1, c2, c3, c4


OPTS = {
    'A': lambda l, c: l['小平'] == '概论',
    'B': lambda l, c: l['乐乐'] == '现代',
    'C': lambda l, c: c['安安'] == '古代',
    'D': lambda l, c: c['小喜'] == '外国',
}

for check_bij in (True, False):
    sols = []
    for lp in itertools.permutations(C):
        lead = dict(zip(P, lp))
        it = itertools.permutations(C) if check_bij else itertools.product(C, repeat=4)
        for cp in it:
            chk = dict(zip(P, cp))
            if any(chk[p] == lead[p] for p in P):   # 检查"另一门"
                continue
            c1, c2, c3, c4 = conds(lead, chk)
            if c1 and c2 and c3 and not c4:
                sols.append((lead, chk))
    print(f'检查是否一一对应={check_bij}：满足(1)(2)(3)且违背(4)的安排数 {len(sols)}')
    for lead, chk in sols:
        print('   主导', lead, ' 检查', chk)
    for k, f in OPTS.items():
        vals = {f(l, c) for l, c in sols}
        print(f'   选项{k}：', '必然成立' if vals == {True} else ('必然不成立' if vals == {False} else '不确定'))
