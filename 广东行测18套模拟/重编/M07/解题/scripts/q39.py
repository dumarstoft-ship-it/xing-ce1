# 第39题：小红今年十多岁；小红5年后 = 小明2年后（小明比小红大3岁）；
# 4年后 2×小红 + 小明 = 平方数的1/3。求小明今年年龄
from math import isqrt
res = []
for x in range(10, 20):           # 十多岁（10也一并检验）
    m = x + 3
    s = 2 * (x + 4) + (m + 4)     # 3x+15
    k2 = 3 * s
    if isqrt(k2) ** 2 == k2:
        res.append((x, m, s, k2))
print(res)                        # [(11, 14, 48, 144)]
assert len(res) == 1 and res[0][1] == 14
# 若误把年龄差方向弄反（小明比小红小3岁）：3x+9 → 9(x+3) 为平方 → x=13，小明10，无对应选项
for x in range(10, 20):
    s = 2 * (x + 4) + (x - 3 + 4)
    if isqrt(3 * s) ** 2 == 3 * s:
        print("方向弄反时:", x, x - 3)
