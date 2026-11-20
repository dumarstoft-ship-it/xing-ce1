"""S02 第43题：容器底面直径20cm，实心圆柱直径10cm、高8cm，装满水后取出（原完全浸没），水面下降多少。
选项 A1 B2 C3 D4"""
from math import pi, isclose
V = pi * 5 ** 2 * 8
drop = V / (pi * 10 ** 2)
print('圆柱体积', V / pi, 'π，水面下降', drop, 'cm')
assert isclose(drop, 2)
print('若误用直径比（10/20）×8：', 10 / 20 * 8, '（D项）；若误用“容器底面积−圆柱底面积”作分母：', 200 / 75)
