"""M05 第33题：1，9/26，4/21，9/62，29/215，（ ）

思路：分母 26=3³−1、215=6³−1，猜测分母为 n³−1（n=2..7）：7,26,63,124,215,342。
反约分：1=7/7，4/21=12/63，9/62=18/124。
分子 7,9,12,18,29：一级差 2,3,6,11，二级差 1,3,5（公差2的等差），下一个二级差7，
一级差 11+7=18，分子 29+18=47，所求项 47/342。
"""
from fractions import Fraction as F

terms = [F(1), F(9, 26), F(4, 21), F(9, 62), F(29, 215)]
options = {"A": F(8, 57), "B": F(47, 342), "C": F(23, 114), "D": F(7, 38)}

dens = [n ** 3 - 1 for n in range(2, 8)]
print("分母 n³−1:", dens)
nums = []
for t, d in zip(terms, dens):
    num = t * d
    assert num.denominator == 1, (t, d)
    nums.append(int(num))
print("对应分子:", nums)
assert nums == [7, 9, 12, 18, 29]


def diffs(s):
    return [b - a for a, b in zip(s, s[1:])]


print("分子一级差:", diffs(nums), "二级差:", diffs(diffs(nums)))
assert diffs(diffs(nums)) == [1, 3, 5]
pred_num = nums[-1] + diffs(nums)[-1] + 7
pred = F(pred_num, dens[-1])
print("预测:", f"{pred_num}/{dens[-1]}", "=", pred)

hits = []
for k, v in options.items():
    num = v * dens[-1]
    ok = v == pred
    print(f"{k} {v}: 化为分母342时分子 {num} -> {'符合' if ok else '不符'}")
    if ok:
        hits.append(k)
assert hits == ["B"], hits

# 题面各项都是约分后的形式，这里确认约分结果一致
assert [F(n, d) for n, d in zip(nums, dens)] == terms
print("答案: B 47/342")
