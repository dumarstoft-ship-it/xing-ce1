"""S02 第45题：第一排21个座位，要求任何一个空座都与已就座者相邻，已就座最少几人。 选项 A6 B7 C8 D9
即21个点的路径上的最小支配集。用动态规划/穷举验证。"""
from itertools import combinations
n = 21
def dominates(S):
    s = set(S)
    return all(i in s or (i - 1) in s or (i + 1) in s for i in range(n))
best = None
for k in range(1, n + 1):
    for S in combinations(range(n), k):
        if dominates(S):
            best = (k, S)
            break
    if best:
        break
print('最少', best[0], '人，一种坐法（座位号）：', [i + 1 for i in best[1]])
assert best[0] == 7
print('从第1号起每隔2个坐一人（1、4、…、19）是否满足：', dominates(range(0, 21, 3)), '→ 还要在第21号旁补一人，共8人（C项）')
print('从第2号起（2、5、…、20）：', dominates(range(1, 21, 3)))
