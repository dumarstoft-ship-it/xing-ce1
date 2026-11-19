"""M09 第41题：6支队平均分为上午组、下午组（各3队），甲、乙不能同组，分组情况共几种？ 选项 A6 B8 C10 D12
核验：枚举上午组的所有3队组合（上午组、下午组是两个不同的组，选定上午组即确定分组）。"""
from itertools import combinations
teams = ['甲', '乙', '丙', '丁', '戊', '己']
all_ways = list(combinations(teams, 3))           # 上午组
ok = [g for g in all_ways if ('甲' in g) != ('乙' in g)]
same = [g for g in all_ways if ('甲' in g) == ('乙' in g)]
print('不加限制：', len(all_ways), '种；甲乙分开：', len(ok), '种；甲乙同组：', len(same), '种')
assert len(ok) == 12
# 不区分上午/下午（只看怎样分成两堆）
unordered_ok = {frozenset([frozenset(g), frozenset(set(teams) - set(g))]) for g in ok}
unordered_all = {frozenset([frozenset(g), frozenset(set(teams) - set(g))]) for g in all_ways}
print('若不区分上午、下午：甲乙分开', len(unordered_ok), '种；不加限制', len(unordered_all), '种')
opts = {'A': 6, 'B': 8, 'C': 10, 'D': 12}
print('答案：', [k for k, v in opts.items() if v == len(ok)])
print('易错对应：不区分上下午→', [k for k, v in opts.items() if v == len(unordered_ok)],
      '；算成甲乙同组的情形→', [k for k, v in opts.items() if v == len(same)],
      '；不区分上下午且不加限制→', [k for k, v in opts.items() if v == len(unordered_all)])
# 公式：甲乙分别去上午、下午有2种，其余4队选2队与甲同组C(4,2)=6 → 2×6=12
from math import comb
assert 2 * comb(4, 2) == 12 and comb(6, 3) - 2 * comb(4, 1) == 12
