"""Q45: totals this month 78, 104, 130 (万元); every employee sold the same amount s >= 20.
Next month each department targets 150. Find (甲 avg) - (丙 avg)."""
from fractions import Fraction as F
tot = {"甲": 78, "乙": 104, "丙": 130}
# s need not be assumed integer: s = 78/a = 104/b = 130/c with integer headcounts
cands = []
for a in range(1, 79):
    s = F(78, a)
    if s < 20:
        break
    if (F(104) / s).denominator == 1 and (F(130) / s).denominator == 1:
        cands.append(s)
print("possible common per-person sales s >= 20:", cands)
assert cands == [26]
s = cands[0]
heads = {k: int(v / s) for k, v in tot.items()}
print("headcounts:", heads)
avg = {k: F(150, n) for k, n in heads.items()}
print("next-month averages:", {k: str(v) for k, v in avg.items()})
# feasibility: integer sales, each >= 20
for k, n in heads.items():
    q, r = divmod(150, n)
    split = [q + 1] * r + [q] * (n - r)
    assert sum(split) == 150 and min(split) >= 20
    print(k, "e.g. split", split)
diff = avg["甲"] - avg["丙"]
# reading where 'same amount' is only within each department -> not unique (shows intended reading)
alt = {k: [n for n in range(1, v + 1) if v % n == 0 and v // n >= 20] for k, v in tot.items()}
print("if only equal within each dept, possible headcounts:", alt)
opts = {"A": 25, "B": 20, "C": 15, "D": 10}
m = [k for k, v in opts.items() if v == diff]
assert m == ["B"], m
print("difference =", diff, "ANSWER:", m[0])
