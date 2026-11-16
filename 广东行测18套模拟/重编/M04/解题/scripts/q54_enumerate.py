# -*- coding: utf-8 -*-
"""Q54 枚举：6 种植物种进 6 个区域。

区域布局（4×4 编码）：
 1 1 1 2
 4 5 5 2
 4 6 6 2
 4 3 3 3
相邻 = 有公共边。1~4 号面积相等（各3格），5、6 号面积相等（各2格）。
"""
import itertools

G = ['1112', '4552', '4662', '4333']
adj = {str(i): set() for i in range(1, 7)}
for r in range(4):
    for c in range(4):
        for dr, dc in ((0, 1), (1, 0)):
            rr, cc = r + dr, c + dc
            if rr < 4 and cc < 4 and G[r][c] != G[rr][cc]:
                adj[G[r][c]].add(G[rr][cc])
                adj[G[rr][cc]].add(G[r][c])
area = {k: sum(row.count(k) for row in G) for k in adj}
print('相邻关系:', {k: sorted(v) for k, v in adj.items()})
print('面积(格数):', area)

plants = ['甲', '乙', '丙', '丁', '戊', '己']
sols = []
for perm in itertools.permutations('123456'):
    pos = dict(zip(plants, perm))
    if area[pos['甲']] != area[pos['丙']] or pos['丙'] in adj[pos['甲']]:
        continue
    if area[pos['乙']] == area[pos['己']] or pos['己'] in adj[pos['乙']]:
        continue
    if len(adj[pos['戊']]) != 3:          # 戊只与另外3种植物相邻（6块地都种了植物）
        continue
    if pos['乙'] != '5':
        continue
    sols.append(pos)
print('乙在5号时的全部方案：')
for s in sols:
    print('  ', s)
claims = {'A 甲在2号': lambda s: s['甲'] == '2', 'B 丁在6号': lambda s: s['丁'] == '6',
          'C 戊在1号': lambda s: s['戊'] == '1', 'D 己在3号': lambda s: s['己'] == '3'}
for k, f in claims.items():
    print(k, '在所有方案中都成立' if all(f(s) for s in sols) else '不一定成立（不能推出）')
