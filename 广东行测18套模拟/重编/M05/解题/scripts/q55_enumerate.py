"""Q55 分析推理：穷举5人各选2门、每门恰2人的全部方案，筛出满足①-⑤的情形，检验各选项是否一定成立。"""
from itertools import combinations, product

people = ['甲', '乙', '丙', '丁', '戊']
courses = ['绘画', '书法', '舞蹈', '唱歌', '陶艺']
pairs = [frozenset(c) for c in combinations(courses, 2)]
sols = []
for choice in product(pairs, repeat=5):
    a = dict(zip(people, choice))
    if any(sum(c in a[p] for p in people) != 2 for c in courses):
        continue
    if '绘画' in a['甲'] or '舞蹈' in a['甲']:
        continue                                                   # ①
    if a['乙'] & a['丙'] or '陶艺' in a['丙']:
        continue                                                   # ②
    if '书法' in a['丁'] or len(a['丁'] & a['戊']) != 1:
        continue                                                   # ③
    if '唱歌' in a['戊'] or a['戊'] & a['甲']:
        continue                                                   # ④
    if a['乙'] != frozenset(['书法', '绘画']):
        continue                                                   # ⑤
    sols.append(a)
print('满足条件的方案数:', len(sols))
for s in sols:
    print('  ', {p: '、'.join(sorted(s[p], key=courses.index)) for p in people})
opts = {'A': ('甲', '陶艺'), 'B': ('丙', '绘画'), 'C': ('丁', '舞蹈'), 'D': ('戊', '陶艺')}
for k, (p, c) in opts.items():
    print('option %s %s报名%s: %s' % (k, p, c, '一定' if all(c in s[p] for s in sols) else '不一定'))
