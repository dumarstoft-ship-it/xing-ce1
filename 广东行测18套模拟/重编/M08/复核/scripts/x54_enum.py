# 第54题：5 人各管 1 个窗口，只能管自己熟悉的业务，枚举全部安排
from itertools import permutations
W = ['登记', '咨询', '报送', '投诉', '综合']
know = {
    '小丽': {'登记'},
    '小马': {'登记', '咨询'},
    '小高': {'报送', '投诉'},
    '老王': set(W) - {'综合', '投诉'},
    '老董': set(W),
}
P = list(know)
sols = [dict(zip(P, perm)) for perm in permutations(W) if all(w in know[p] for p, w in zip(P, perm))]
print('可行安排数：', len(sols))
for s in sols:
    print(s)
checks = {
    'A 老董不负责综合': lambda s: s['老董'] != '综合',
    'B 小高负责报送': lambda s: s['小高'] == '报送',
    'C 小马不负责咨询': lambda s: s['小马'] != '咨询',
    'D 老王负责报送': lambda s: s['老王'] == '报送',
}
for k, f in checks.items():
    print(k, '：在所有可行安排中恒真' if all(f(s) for s in sols) else ('：恒假' if not any(f(s) for s in sols) else '：可能'))
