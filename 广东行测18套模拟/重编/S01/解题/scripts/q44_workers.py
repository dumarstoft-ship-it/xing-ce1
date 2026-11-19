"""S01 第44题：三道工序每人每小时5、4、8件，使三道工序每小时产量相同，至少要几名工人。 选项 A17 B20 C23 D40"""
from math import lcm
best = None
for q in range(1, 200):                 # q：每道工序每小时产量
    if q % 5 == 0 and q % 4 == 0 and q % 8 == 0:
        best = (q, q // 5, q // 4, q // 8)
        break
print('每小时产量', best[0], '各工序人数', best[1:], '共', sum(best[1:]))
assert best[0] == lcm(5, 4, 8) == 40 and sum(best[1:]) == 23
print('易错核对：最小公倍数本身为', lcm(5, 4, 8), '（D项），是每小时件数而非人数')
