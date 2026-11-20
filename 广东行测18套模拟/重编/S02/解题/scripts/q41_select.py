"""S02 第41题：6男4女选5人，至少3名女职工，组合数。 选项 A60 B66 C120 D132"""
from itertools import combinations
people = ['M%d' % i for i in range(6)] + ['F%d' % i for i in range(4)]
cnt = sum(1 for c in combinations(people, 5) if sum(p[0] == 'F' for p in c) >= 3)
print(cnt)
assert cnt == 66
from math import comb
print('恰3女', comb(4, 3) * comb(6, 2), '恰4女', comb(4, 4) * comb(6, 1), '；只算恰3女得60（A）')
