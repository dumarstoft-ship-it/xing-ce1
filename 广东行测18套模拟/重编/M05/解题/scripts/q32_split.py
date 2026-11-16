"""M05 第32题：5.4，9.1，10.8，18.2，20.16，（ ）

思路：机械拆分。把每项拆成整数部分和小数部分（小数点后的数字整体看作一个数）：
  整数部分 5,9,10,18,20；小数部分 4,1,8,2,16。
两部分都是奇数项、偶数项分别×2 的交叉数列。逐个检验选项。
另外整体看偶数项 9.1、18.2 本身就是×2，下一项 36.4 也吻合。
"""
from decimal import Decimal

seq = ["5.4", "9.1", "10.8", "18.2", "20.16"]
options = {"A": "36.4", "B": "36.28", "C": "35.4", "D": "33.15"}


def split(s):
    i, d = s.split(".")
    return int(i), int(d)


ints = [split(s)[0] for s in seq]
decs = [split(s)[1] for s in seq]
print("整数部分:", ints)
print("小数部分:", decs)


def interleaved_double(s):
    """奇数项、偶数项各自成公比2的等比数列"""
    odd, even = s[0::2], s[1::2]
    return all(b == 2 * a for a, b in zip(odd, odd[1:])) and all(b == 2 * a for a, b in zip(even, even[1:]))


assert interleaved_double(ints) and interleaved_double(decs)

hits = []
for k, v in options.items():
    i, d = split(v)
    ok = interleaved_double(ints + [i]) and interleaved_double(decs + [d])
    print(f"{k} {v}: 整数部分 {i}，小数部分 {d} -> {'符合' if ok else '不符'}")
    if ok:
        hits.append(k)
assert hits == ["A"], hits

# 旁证1：整体看偶数项 9.1 -> 18.2 -> 36.4，每次×2
assert Decimal("9.1") * 2 == Decimal("18.2") and Decimal("18.2") * 2 == Decimal("36.4")
# 旁证2：奇数项整体×2 不成立（10.8×2=21.6≠20.16），说明是拆分规律而非整体倍数
print("10.8×2 =", Decimal("10.8") * 2, "≠ 20.16，故按整数、小数两部分分别看")
# 旁证3：每项整数部分+小数部分 = 下一项整数部分
sums = [i + d for i, d in zip(ints, decs)]
print("各项 整数+小数:", sums, "（与下一项整数部分 9,10,18,20,36 吻合）")
assert sums[:-1] == ints[1:] and sums[-1] == 36

print("答案: A 36.4")
