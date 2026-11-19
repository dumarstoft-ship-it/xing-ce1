"""M10 第53、57、61题：枚举所有可能情形，检验各选项是否“必然为真”。"""
import itertools

# ---- 第53题：3人 × 3村 × 3专业 ----
people = ['蒋', '陈', '刘']
sols = []
for vil in itertools.permutations('甲乙丙'):
    for maj in itertools.permutations(['农学', '法学', '工学']):
        v = dict(zip(people, vil)); m = dict(zip(people, maj))
        vm = {v[p]: m[p] for p in people}
        if v['陈'] == '甲': continue
        if vm['甲'] == '农学': continue
        if vm['丙'] != '工学': continue
        if m['陈'] == '农学': continue
        sols.append((v, m))
print('第53题 满足条件的情形数', len(sols))
opts = {'A 刘去甲': lambda v, m: v['刘'] == '甲', 'B 蒋去乙': lambda v, m: v['蒋'] == '乙',
        'C 刘是工学': lambda v, m: m['刘'] == '工学', 'D 陈是工学': lambda v, m: m['陈'] == '工学'}
for k, f in opts.items():
    n = sum(f(v, m) for v, m in sols)
    print(f'  {k}: 成立 {n}/{len(sols)}')

# ---- 第57题：每人看作4个属性的组合（干部/工勤、博士、统计学、男），枚举出现哪些“类型” ----
types = list(itertools.product([0, 1], repeat=4))  # (干部, 博士, 统计, 男)
res = {k: True for k in 'ABCD'}
cnt = 0
for mask in range(1, 1 << 16):
    present = [t for i, t in enumerate(types) if mask >> i & 1]
    if not any(t[0] for t in present) or not any(not t[0] for t in present):
        continue  # 干部、工勤人员都有
    if not any(t[0] and t[1] for t in present):
        continue  # 有（多名）干部是博士
    if not any(t[1] and not t[2] for t in present):
        continue  # 有的博士不是统计学专业毕业
    if any(t[3] and not t[2] for t in present):
        continue  # 所有男性都是统计学专业毕业
    cnt += 1
    res['A'] &= any(t[3] and not t[1] for t in present)
    res['B'] &= any(t[1] and not t[3] for t in present)
    res['C'] &= any(t[3] and not t[0] for t in present)
    res['D'] &= any(t[0] and not t[2] for t in present)
print('第57题 满足条件的情形数', cnt, '；各项是否必然为真', res)

# ---- 第61题：女党员a、女群众b、男党员c、男群众d ----
ok = {k: True for k in 'ABCD'}
cex = {}
for a, b, c, d in itertools.product(range(0, 8), repeat=4):
    if a + b > c + d and a + c > b + d:
        checks = {'A': b > d, 'B': c > a, 'C': a > d, 'D': d > c}
        for k, val in checks.items():
            if not val:
                ok[k] = False
                cex.setdefault(k, (a, b, c, d))
print('第61题 各项是否必然为真', ok, '；反例(女党员,女群众,男党员,男群众)', cex)
print('  文中所举反例 (5,1,3,2):', 5 + 1 > 3 + 2 and 5 + 3 > 1 + 2, '→ A', 1 > 2, 'B', 3 > 5, 'D', 2 > 3)
