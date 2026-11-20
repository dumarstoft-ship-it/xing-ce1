"""M11 第42题：行政部2人、人事部3人中随机选2人，都来自人事部的概率。 选项 A10% B20% C30% D40%"""
from itertools import combinations
from fractions import Fraction as F
people = ['行1', '行2', '人1', '人2', '人3']
pairs = list(combinations(people, 2))
fav = [p for p in pairs if all(x[0] == '人' for x in p)]
p = F(len(fav), len(pairs))
print(len(pairs), len(fav), p)
assert p == F(3, 10)
print('两人都来自行政部的概率', F(1, 10), '（A项）')
