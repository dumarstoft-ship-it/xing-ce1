"""M09 第42题：6个社区中2个不通过，随机抽3个，既有通过又有不通过的概率？ 选项 A1/5 B1/2 C2/3 D4/5
核验：枚举C(6,3)=20种抽法。"""
from itertools import combinations
from fractions import Fraction as F
comm = ['P1', 'P2', 'P3', 'P4', 'F1', 'F2']    # P通过，F不通过
draws = list(combinations(comm, 3))
mixed = [d for d in draws if any(c[0] == 'P' for c in d) and any(c[0] == 'F' for c in d)]
allP = [d for d in draws if all(c[0] == 'P' for c in d)]
p = F(len(mixed), len(draws))
print('总抽法', len(draws), '；混合', len(mixed), '；全通过', len(allP), '；概率', p)
assert p == F(4, 5)
opts = {'A': F(1, 5), 'B': F(1, 2), 'C': F(2, 3), 'D': F(4, 5)}
print('答案：', [k for k, v in opts.items() if v == p])
print('易错：只算“全部通过”的概率', F(len(allP), len(draws)), '→', [k for k, v in opts.items() if v == F(len(allP), len(draws))])
only_one_fail = F(2 * 6, 20)
print('只算“恰1个不通过”：', only_one_fail, '（不在选项中）')
