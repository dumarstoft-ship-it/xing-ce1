"""第34题：5/12，43/96，1/2，55/96，2/3，（ ）  选项 A29/32 B25/32 C11/16 D11/12

核验思路：通分到 96，看分子规律；再把四个选项也通分，检查哪个分子符合。
"""
from fractions import Fraction as F

seq = [F(5, 12), F(43, 96), F(1, 2), F(55, 96), F(2, 3)]
options = {"A": F(29, 32), "B": F(25, 32), "C": F(11, 16), "D": F(11, 12)}

nums = [x * 96 for x in seq]
assert all(n.denominator == 1 for n in nums)
nums = [int(n) for n in nums]
print("通分到96后的分子", nums)                    # 40 43 48 55 64
d1 = [nums[i + 1] - nums[i] for i in range(4)]
print("分子一级差", d1)                             # 3 5 7 9
print("分子 - n^2:", [nums[i] - (i + 1) ** 2 for i in range(5)])  # 恒为39
nxt = nums[-1] + d1[-1] + 2
print("下一分子", nxt, "=> 下一项", F(nxt, 96))
for k, v in options.items():
    print(k, v, "通分后分子", v * 96, "符合" if v == F(nxt, 96) else "")
