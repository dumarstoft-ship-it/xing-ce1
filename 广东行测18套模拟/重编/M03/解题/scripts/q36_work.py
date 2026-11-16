"""Q36: jia's solo time is half of yi's  -> eff(jia) = 2*eff(yi).
3 days of bing = 4 days of jia + 2 days of yi.
Plan: jia 4 days, then yi 2 days, then bing 4 days -> done (plan length 4+2+4 = 10 days).
Actual: jia absent; yi and bing finish it. Minimum days bing must work so total <= 10 days?
options A2 B3 C4 D6"""
from fractions import Fraction as F
import math

yi = F(3)
jia = 2 * yi
bing = (4 * jia + 2 * yi) / 3
total = 4 * jia + 2 * yi + 4 * bing
plan_days = 4 + 2 + 4
print(f"eff jia={jia}, yi={yi}, bing={bing}; total work={total}; plan days={plan_days}")
assert (jia, yi, bing, total) == (6, 3, 10, 70)

# yi and bing may each work any whole number of days within the 10-day window.
best = None
for bing_days in range(0, plan_days + 1):
    for yi_days in range(0, plan_days + 1):
        if yi_days * yi + bing_days * bing >= total:
            best = bing_days if best is None else min(best, bing_days)
print("minimum whole days for bing (yi works at most 10 days):", best)
assert best == 4

# Fractional check: bing_days >= (70 - 3*10)/10 = 4 exactly.
need = (total - plan_days * yi) / bing
print("exact minimum (yi works all 10 days):", need)
assert need == 4

# Trap reading: both work together from day 1 until done -> 70/13 days (~5.38) -> '6 days'.
together = total / (yi + bing)
print("if they always work together:", together, "~", float(together), "-> ceil", math.ceil(together))

opts = {"A": 2, "B": 3, "C": 4, "D": 6}
matches = [k for k, v in opts.items() if v == best]
assert matches == ["C"], matches
print("ANSWER:", matches[0])
