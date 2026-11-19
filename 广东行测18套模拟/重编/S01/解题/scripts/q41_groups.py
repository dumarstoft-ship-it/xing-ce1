"""S01 第41题：男女各3名志愿者，平均分到2个社区（每社区3人），每社区至少1名女性，求组合数。
选项 A18 B24 C32 D38"""
from itertools import combinations
people = ['M1', 'M2', 'M3', 'F1', 'F2', 'F3']
cnt = 0
for g1 in combinations(people, 3):      # 社区一的3人，其余去社区二（两个社区不同）
    g2 = [x for x in people if x not in g1]
    if any(x[0] == 'F' for x in g1) and any(x[0] == 'F' for x in g2):
        cnt += 1
print('组合数', cnt)
assert cnt == 18 == 20 - 2 == 3 * 3 + 3 * 3
