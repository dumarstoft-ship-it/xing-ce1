"""第39题：红r、白3r、绿4，黄y = (1+5/9)×(r+3r+4)，总数 ≤ 100，求 y − r。枚举全部可能。"""
from fractions import Fraction as F

sols = []
for r in range(0, 101):
    others = r + 3 * r + 4
    y = F(14, 9) * others
    if y.denominator != 1:
        continue
    y = int(y)
    total = y + others
    if total <= 100 and r >= 1:
        sols.append((r, y, 3 * r, 4, total))
print("(红, 黄, 白, 绿, 总数):", sols)
assert len(sols) == 1
r, y = sols[0][0], sols[0][1]
print("黄 − 红 =", y - r)
options = {"A": 40, "B": 44, "C": 48, "D": 52}
hits = [k for k, v in options.items() if v == y - r]
assert hits == ["C"]
print("答案:", hits)
