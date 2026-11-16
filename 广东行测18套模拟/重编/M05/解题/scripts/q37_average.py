"""M05 第37题：高一平均70，高二平均90，总平均82；去掉高一最低两人（平均50）后两年级平均分相等。
求两年级人数差。枚举人数，并构造一组满足"满分100"的具体分数检验可行性。
"""
from fractions import Fraction as F

sols = []
for n1 in range(3, 501):          # 高一至少3人，去掉两人后还有人
    for n2 in range(1, 501):
        if F(70 * n1 + 90 * n2, n1 + n2) != 82:
            continue
        if F(70 * n1 - 2 * 50, n1 - 2) != 90:
            continue
        sols.append((n1, n2))
print("满足条件的(高一人数,高二人数):", sols)
assert sols == [(4, 6)]
n1, n2 = sols[0]
print("人数差:", n2 - n1)

# 可行性：高一4人总分280，最低两人共100分，其余两人共180分；高二6人共540分
g1 = [50, 50, 90, 90]
g2 = [90] * 6
assert sum(g1) == 280 and sum(g2) == 540 and max(g1 + g2) <= 100
assert sorted(g1)[:2] == [50, 50]
assert F(sum(g1[2:]), 2) == F(sum(g2), 6) == 90
assert F(sum(g1) + sum(g2), 10) == 82
print("示例分数可行:", g1, g2)
print("答案: B 2")
