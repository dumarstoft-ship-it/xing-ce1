"""M08 第41题：9页中3页有错字，且这3页中有2页页码连续；求页码为3的倍数的页(3,6,9)都没有错字的概率。
枚举全部三页组合。“有2页连续”按“恰有2页相邻、第3页与它们都不相邻”理解；同时给出“至少2页相邻”的结果作对照。"""
from itertools import combinations
from fractions import Fraction as F
opts = {'A': F(2, 7), 'B': F(2, 5), 'C': F(1, 2), 'D': F(5, 7)}
def adj_pairs(s): return sum(1 for a, b in combinations(s, 2) if abs(a-b) == 1)
allc = list(combinations(range(1, 10), 3))
exactly = [s for s in allc if adj_pairs(s) == 1]
atleast = [s for s in allc if adj_pairs(s) >= 1]
good = lambda s: all(p % 3 for p in s)
pe = F(sum(good(s) for s in exactly), len(exactly))
pa = F(sum(good(s) for s in atleast), len(atleast))
print('恰有2页相邻: 样本', len(exactly), '有利', sum(good(s) for s in exactly), '概率', pe)
print('至少2页相邻: 样本', len(atleast), '有利', sum(good(s) for s in atleast), '概率', pa)
print('有利组合:', [s for s in exactly if good(s)])
assert [k for k, v in opts.items() if v == pe] == ['A']
assert pa not in opts.values()
# 错误思路：样本空间取 C(9,3)=84
print('若忽略“有2页连续”: ', F(sum(good(s) for s in allc), len(allc)))
print('若样本按“选一对相邻页(8种)×第3页(7种)=56”计: 有利按 3对×4 =12 → ', F(12, 56))
