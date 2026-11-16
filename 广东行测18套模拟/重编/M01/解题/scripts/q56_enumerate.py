# 第56题：5人分到3个岗位，枚举全部分配，验证“丁在服务岗”时哪项一定为真
import itertools
people = ['甲', '乙', '丙', '丁', '戊']
posts = ['综合', '执法', '服务']
sols = []
for assign in itertools.product(posts, repeat=5):
    a = dict(zip(people, assign))
    cnt = {p: assign.count(p) for p in posts}
    if not all(1 <= cnt[p] <= 2 for p in posts): continue          # (1)
    if a['甲'] != '综合' and a['乙'] != '执法': continue             # (2) 甲不在综合 → 乙在执法
    if a['丙'] == a['戊']: continue                                   # (3)
    if not cnt['执法'] > cnt['服务']: continue                         # (4)
    if a['丁'] != '服务': continue                                    # 附加条件
    sols.append(a)
print('满足全部条件的分配数:', len(sols))
for s in sols: print('  ', s)
opts = {'A 甲在综合岗': lambda a: a['甲'] == '综合',
        'B 乙不在执法岗': lambda a: a['乙'] != '执法',
        'C 丙在执法岗': lambda a: a['丙'] == '执法',
        'D 戊不在综合岗': lambda a: a['戊'] != '综合'}
for k, f in opts.items():
    print(k, '一定为真' if all(f(s) for s in sols) else ('可能为真' if any(f(s) for s in sols) else '一定为假'))
