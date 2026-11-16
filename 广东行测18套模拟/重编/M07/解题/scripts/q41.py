# 第41题：1月利润率50%；2月售价降20%，销量多16个；两月销售额均960元。求两月总利润
from fractions import Fraction as F
sols = []
for q in range(1, 961):           # 1月销量
    p = F(960, q)                 # 1月单价
    if F(4, 5) * p * (q + 16) == 960:
        cost = p / F(3, 2)
        profit = (p - cost) * q + (F(4, 5) * p - cost) * (q + 16)
        sols.append((q, p, cost, profit))
print(sols)                       # [(64, 15, 10, 480)]
assert len(sols) == 1 and sols[0][3] == 480
q, p, cost, _ = sols[0]
print("1月利润", (p - cost) * q, "2月利润", (F(4, 5) * p - cost) * (q + 16))
# 错误思路：把利润率当成“利润/售价”→ 成本=7.5，总利润=840（无对应选项）；只算1月利润=320（无对应选项）
c2 = p / 2
print("利润/售价口径：", (p - c2) * q + (F(4, 5) * p - c2) * (q + 16))
