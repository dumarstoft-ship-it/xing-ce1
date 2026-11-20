"""M11 第53、57、61题：枚举检验。"""
import itertools

# ---- 第53题：赵+钱=孙+李，赵+李>钱+孙，钱>赵+孙（数量取 1～20） ----
orders = set()
for z, q, s, l in itertools.product(range(1, 21), repeat=4):
    if z + q == s + l and z + l > q + s and q > z + s:
        orders.add(tuple(sorted(['赵', '钱', '孙', '李'], key=lambda n: -{'赵': z, '钱': q, '孙': s, '李': l}[n])))
print('第53题 满足条件的由多到少顺序：', orders)

# ---- 第57题：每人看作 (电竞毕业生, 支持赛事, 喜欢游戏, 体育频道, 50岁以上) 的组合 ----
# 先按三条“所有……”筛出允许出现的人的类型，再枚举这些类型的全部组合（存在性条件只看出现哪些类型）
allowed = [t for t in itertools.product([0, 1], repeat=5)
           if not (t[0] and not t[1]) and not (t[1] and not t[2]) and not (t[4] and t[2])]
ok = {k: True for k in 'ABCD'}; n = 0
for r in range(1, len(allowed) + 1):
    for present in itertools.combinations(allowed, r):
        if not any(e and tv for e, s, g, tv, o in present): continue     # 有的电竞毕业生在体育频道
        if not any(tv and o for e, s, g, tv, o in present): continue     # 体育频道有50岁以上的人
        n += 1
        ok['A'] &= not any(o and s for e, s, g, tv, o in present)
        ok['B'] &= any(tv and g for e, s, g, tv, o in present)
        ok['C'] &= any(e and o for e, s, g, tv, o in present)
        ok['D'] &= all(g for e, s, g, tv, o in present if e)
print('第57题 允许的类型', len(allowed), '个，满足题干的组合', n, '种；各项能否推出', ok,
      '；电竞毕业生且50岁以上的类型是否允许：', any(t[0] and t[4] for t in allowed))

# ---- 第61题：甲乙丙丁 × (硕士, 注会, 高职) ----
P = '甲乙丙丁'; sols = []
for bits in itertools.product(itertools.product([0, 1], repeat=3), repeat=4):
    d = dict(zip(P, bits))
    M = [p for p in P if d[p][0]]; C = [p for p in P if d[p][1]]; H = [p for p in P if d[p][2]]
    allthree = [p for p in P if all(d[p])]
    if len(allthree) != 1 or len(M) != 3 or len(C) != 2 or len(H) != 1: continue
    if any(not any(d[p]) for p in P): continue
    if d['甲'][0] != d['丁'][0] or d['乙'][1] != d['丙'][1]: continue
    if d['丙'][0] + d['丁'][0] != 1: continue
    sols.append((d, allthree[0]))
print('第61题 解的个数', len(sols), '；三项都有的人', {s[1] for s in sols})
