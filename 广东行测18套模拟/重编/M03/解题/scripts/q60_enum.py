# 第60题 枚举验证：7名选手排名（1=最快），无并列
from itertools import permutations

names = ['猎豹', '兔子', '狮子', '马', '羚羊', '狼', '鹿']
sols = []
for p in permutations(range(1, 8)):
    r = dict(zip(names, p))
    if r['猎豹'] != 4:                                   # (1)
        continue
    if not (r['狮子'] < r['兔子'] < r['马']):            # (2) 兔比狮慢、比马快
        continue
    if not (r['羚羊'] < r['猎豹'] < r['狼']):            # (3) 猎豹比羚羊慢、比狼快
        continue
    if (r['狮子'] == 2 or r['羚羊'] == 3) and r['狼'] != 1:   # (4)
        continue
    if (r['羚羊'] == 2 or r['兔子'] == 6) and r['马'] != 3:   # (5)
        continue
    sols.append(r)

print('全部可行排名：')
for s in sols:
    print('  ', sorted(s, key=s.get))

opts = {
    'A 兔子比狼快': lambda r: r['兔子'] < r['狼'],
    'B 猎豹比兔子快': lambda r: r['猎豹'] < r['兔子'],
    'C 狮子比鹿快': lambda r: r['狮子'] < r['鹿'],
    'D 羚羊比狮子快': lambda r: r['羚羊'] < r['狮子'],
}
for k, f in opts.items():
    n = sum(f(s) for s in sols)
    print(k, f'成立于 {n}/{len(sols)} 种方案', '-> 不可能' if n == 0 else '')
