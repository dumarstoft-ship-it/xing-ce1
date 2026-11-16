"""第56题：枚举“主导”与“检查”两种分工，检验在违背条件(4)（即 小喜检查古代 且 安安主导外国）时哪项一定为真。
主导是一人一门的一一对应；检查：每人检查一门且不是自己主导的那门。
分两种口径枚举：①检查也是一一对应（每门课恰有一人检查）；②只要求每人检查一门别的课。"""
import itertools
P = ['小平', '安安', '小喜', '乐乐']
C = ['古代', '外国', '现汉', '概论']

def conds(lead, chk):
    c1 = not (lead['小平'] == '古代') or chk['小喜'] == '外国'
    c2 = not (lead['安安'] == '外国') or chk['乐乐'] == '概论'
    c3 = not (lead['小喜'] == '概论') or lead['乐乐'] == '外国'
    violate4 = chk['小喜'] == '古代' and lead['安安'] == '外国'
    return c1 and c2 and c3 and violate4

opts = {
    'A': lambda l, c: l['小平'] == '概论',
    'B': lambda l, c: l['乐乐'] == '现汉',
    'C': lambda l, c: c['安安'] == '古代',
    'D': lambda l, c: c['小喜'] == '外国',
}
for mode in ('检查一一对应', '检查不要求一一对应'):
    sols = []
    for lp in itertools.permutations(C):
        lead = dict(zip(P, lp))
        chk_iter = itertools.permutations(C) if mode == '检查一一对应' else itertools.product(C, repeat=4)
        for cp in chk_iter:
            chk = dict(zip(P, cp))
            if any(chk[p] == lead[p] for p in P):
                continue
            if conds(lead, chk):
                sols.append((lead, chk))
    print(f'【{mode}】满足的安排数: {len(sols)}')
    for l, c in sols[:4]:
        print('   主导', l, ' 检查', c)
    for k, f in opts.items():
        print('  ', k, '一定为真' if all(f(l, c) for l, c in sols) else '不一定/不成立')
