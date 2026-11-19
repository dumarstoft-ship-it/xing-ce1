"""S01 第42题：6道菜，甲乙丙各随机选2道，三人所选菜品完全不同（两两无重复）的概率。
选项 A不到2% B2%—3% C3%—4% D超过4%"""
from fractions import Fraction as F
from itertools import combinations, product
pairs = list(combinations(range(6), 2))
total = fav = 0
for a, b, c in product(pairs, repeat=3):
    total += 1
    if len(set(a) | set(b) | set(c)) == 6:
        fav += 1
p = F(fav, total)
print('总数', total, '有利', fav, '概率', p, '= %.4f%%' % (float(p) * 100))
assert p == F(15 * 6 * 1, 15 ** 3) == F(2, 75)
assert 0.02 < p < 0.03
# 另一种（不取的）读法：三人选的“组合”两两不同
q = F(15 * 14 * 13, 15 ** 3)
print('若只要求三人所选组合互不相同：%.2f%%' % (float(q) * 100))
