"""M05 第36题：投篮比赛，每人10投，中一次3分。三人共51分，甲比乙多9分，丙是乙的1.5倍。
问甲比丙多投中几次。枚举三人投中次数 0..10。
"""
from fractions import Fraction as F

sols = []
for a in range(11):
    for b in range(11):
        for c in range(11):
            sa, sb, sc = 3 * a, 3 * b, 3 * c
            if sa + sb + sc == 51 and sa - sb == 9 and F(sc) == F(3, 2) * sb:
                sols.append((a, b, c))
print("满足条件的(甲,乙,丙)投中次数:", sols)
assert sols == [(7, 4, 6)]
a, b, c = sols[0]
print("得分:", 3 * a, 3 * b, 3 * c, "甲比丙多投中", a - c, "次")
assert a - c == 1
print("答案: A 1")
