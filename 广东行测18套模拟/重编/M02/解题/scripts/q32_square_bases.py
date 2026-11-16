"""第32题：16，4，36，64，196，（ ）  选项 A441 B484 C576 D625

核验思路：各项均为平方数，取底数后看底数的规律；再逐一检查选项的底数是否满足同一规律。
"""
from math import isqrt

seq = [16, 4, 36, 64, 196]
options = {"A": 441, "B": 484, "C": 576, "D": 625}

bases = [isqrt(x) for x in seq]
assert all(b * b == x for b, x in zip(bases, seq))
print("底数", bases)  # [4, 2, 6, 8, 14]
print("前两项之和=第三项:", [bases[i - 2] + bases[i - 1] == bases[i] for i in range(2, 5)])
nb = bases[-2] + bases[-1]
print("下一底数", nb, "下一项", nb * nb)

for k, v in options.items():
    b = isqrt(v)
    print(k, v, "=%d^2" % b if b * b == v else "非平方数",
          "符合" if b * b == v and b == bases[-2] + bases[-1] else "不符合")

# 原数列直接作差、作商都无规律（对照）
print("原数列作差", [seq[i + 1] - seq[i] for i in range(4)])
print("原数列作商", [round(seq[i + 1] / seq[i], 3) for i in range(4)])
