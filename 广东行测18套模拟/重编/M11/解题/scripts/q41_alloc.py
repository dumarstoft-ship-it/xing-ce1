"""M11 第41题：10台相同电脑分给甲乙丙，每部门至少1台、至多5台，分配方法数。 选项 A9 B12 C18 D27"""
ways = [(a, b, 10 - a - b) for a in range(1, 6) for b in range(1, 6) if 1 <= 10 - a - b <= 5]
print(len(ways), ways)
assert len(ways) == 18
# 隔板法：至少1台 C(9,2)=36，减去某部门≥6台 3×C(4,2)=18
from math import comb
assert comb(9, 2) - 3 * comb(4, 2) == 18
# 易错核对：漏掉“每部门至少1台”（允许0台）且至多5台：
print('允许0台时', sum(1 for a in range(0, 6) for b in range(0, 6) if 0 <= 10 - a - b <= 5))
