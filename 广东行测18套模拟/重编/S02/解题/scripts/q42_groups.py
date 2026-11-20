"""S02 第42题：3个2人组、3个3人组、1个5人组，任选3组，人数和为3的倍数的概率。
选项 A不到15% B15%—25% C25%—35% D超过35%"""
from itertools import combinations
from fractions import Fraction as F
sizes = [2, 2, 2, 3, 3, 3, 5]
picks = list(combinations(range(7), 3))
fav = [p for p in picks if sum(sizes[i] for i in p) % 3 == 0]
pr = F(len(fav), len(picks))
print('总数', len(picks), '有利', len(fav), [tuple(sizes[i] for i in p) for p in fav], '概率', pr, '%.2f%%' % (float(pr) * 100))
assert pr == F(1, 7) and pr < F(15, 100)
