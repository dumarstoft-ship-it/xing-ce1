"""M10 第41题：3男3女站成一列，3名男职工不能全部连在一起，求站法数。 选项 A432 B504 C576 D720"""
from itertools import permutations
people = ['M1', 'M2', 'M3', 'F1', 'F2', 'F3']
cnt = together = 0
for p in permutations(people):
    pos = sorted(i for i, x in enumerate(p) if x[0] == 'M')
    if pos[2] - pos[0] == 2:
        together += 1
    else:
        cnt += 1
print('总数720，男职工全部相邻', together, '，不全相邻', cnt)
assert together == 4 * 3 * 2 * 6 and cnt == 576
# 对照：男职工两两不相邻（插空）有 3!×A(4,3)=144 种，与“全部相邻”恰好同为144
no_adj = sum(1 for p in permutations(people)
             if all(abs(i - j) > 1 for i in range(6) for j in range(6)
                    if i != j and p[i][0] == 'M' and p[j][0] == 'M'))
print('男职工两两不相邻', no_adj)
# 正面分类核对：恰有两名男职工相邻 / 三人两两不相邻 / 三人全相邻
from itertools import combinations
cls = {'恰两人相邻': 0, '两两不相邻': 0, '三人全相邻': 0}
for pos in combinations(range(6), 3):
    g1, g2 = pos[1] - pos[0], pos[2] - pos[1]
    key = '三人全相邻' if g1 == g2 == 1 else ('两两不相邻' if g1 > 1 and g2 > 1 else '恰两人相邻')
    cls[key] += 36                      # 男3!×女3!
print(cls)
assert cls == {'恰两人相邻': 432, '两两不相邻': 144, '三人全相邻': 144}
print('只算“恰两人相邻”得432（A）；432+144=576（C）')
