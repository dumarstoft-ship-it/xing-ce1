"""M10 第44题：23队抽签两两比赛，单数时一队轮空直接晋级，直到决出冠军，共几次轮空。 选项 A2 B3 C4 D5"""
n, byes, rounds = 23, 0, []
while n > 1:
    b = n % 2
    rounds.append((n, n // 2, b))
    byes += b
    n = n // 2 + b
for r in rounds:
    print('本轮%2d队：%2d场比赛，轮空%d队' % r)
print('轮空次数', byes)
assert byes == 2
