"""M09 第39题：A成本1.6售价2.3，B成本2售价3，共9000个，总成本≤15000，利润最大时A生产多少？
选项 A0 B6000 C7500 D9000
核验：以“角”为单位用整数计算，枚举A的产量x=0…9000，满足成本约束的取利润最大者。"""
best = None
for x in range(0, 9001):
    y = 9000 - x
    cost = 16 * x + 20 * y          # 角
    if cost > 150000:
        continue
    profit = 7 * x + 10 * y         # 角
    if best is None or profit > best[1]:
        best = (x, profit, cost)
print('最优：A=%d个，利润=%.1f元，成本=%.1f元' % (best[0], best[1] / 10, best[2] / 10))
assert best[0] == 7500
opts = {'A': 0, 'B': 6000, 'C': 7500, 'D': 9000}
for k, x in opts.items():
    y = 9000 - x
    cost = (16 * x + 20 * y) / 10
    print(f'{k}: A={x}, 成本={cost:.0f}{"(超出15000)" if cost > 15000 else ""}, 利润={(7*x+10*y)/10:.0f}')
# 推理：全做B成本18000，超3000；每把1个B换成A省0.4元 → 至少换7500个；B单件利润1元>A的0.7元，故A越少越好
from fractions import Fraction as F
assert (2 * 9000 - 15000) / (F(2) - F(16, 10)) == 7500
