"""M09 第45题：8队双循环（每两队踢两场），胜3平1负0，第一名最多比第二名多几分？ 选项 A40 B30 C20 D10
核验：
1. 上界：第一名最多14场全胜=42分；其余7队之间有7×6/2×2=42场，每场至少产生2分（平局），
   7队总分≥84，平均≥12，所以第二名≥12分，差≤30；
2. 构造：第一名全胜，其余7队之间全部打平，各得12分，差恰为30；
3. 小规模穷举：4队双循环（12场，3^12种结果）穷举最大分差，与同一公式6(n−1)−2(n−2)比对。"""
from itertools import combinations, product

def max_gap_bruteforce(n):
    games = [(i, j) for i, j in combinations(range(n), 2) for _ in range(2)]
    best = -1
    for res in product((0, 1, 2), repeat=len(games)):   # 0:前者胜 1:平 2:后者胜
        pts = [0] * n
        for (i, j), r in zip(games, res):
            if r == 0: pts[i] += 3
            elif r == 1: pts[i] += 1; pts[j] += 1
            else: pts[j] += 3
        s = sorted(pts, reverse=True)
        best = max(best, s[0] - s[1])
    return best

formula = lambda n: 3 * 2 * (n - 1) - 2 * (n - 2)
for n in (3, 4):
    bf = max_gap_bruteforce(n)
    print(f'{n}队双循环：穷举最大分差={bf}，公式={formula(n)}')
    assert bf == formula(n)

# 8队：构造验证
n = 8
pts = [0] * n
for i, j in combinations(range(n), 2):
    for _ in range(2):
        if i == 0: pts[0] += 3          # 第一名全胜
        else: pts[i] += 1; pts[j] += 1  # 其余全平
print('8队构造积分：', pts)
s = sorted(pts, reverse=True)
gap = s[0] - s[1]
print('第一名', s[0], '第二名', s[1], '差', gap, '；公式', formula(8))
assert gap == formula(8) == 30
opts = {'A': 40, 'B': 30, 'C': 20, 'D': 10}
print('答案：', [k for k, v in opts.items() if v == gap])
# 若误按单循环（每两队一场）：第一名21分，其余各6分，差15（不在选项中）
