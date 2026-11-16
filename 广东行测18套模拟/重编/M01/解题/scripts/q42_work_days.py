"""Q42: A alone 24 days, B alone 36 days. A works 6 days alone, then B joins; during
cooperation B's efficiency is reduced by 1/3. Total days (a partial day counts as a day)."""
from fractions import Fraction as F
import math
W = 72                       # LCM of 24 and 36
a, b = F(W, 24), F(W, 36)    # 3 and 2 per day
b_low = b * (1 - F(1, 3))    # 4/3 per day
left = W - 6 * a
coop = left / (a + b_low)
total = 6 + coop
print("A per day", a, " B per day", b, " B reduced", b_low)
print("left after 6 days:", left, " cooperation days:", coop, "=", float(coop))
print("total exact:", total, "=", float(total), "-> rounded up:", math.ceil(total))
# day-by-day simulation as a cross-check
done, day = F(0), 0
while done < W:
    day += 1
    done += a if day <= 6 else a + b_low
print("simulation: finished during day", day)
assert day == math.ceil(total) == 19
opts = {"A": 12, "B": 13, "C": 18, "D": 19}
m = [k for k, v in opts.items() if v == day]
print("traps: cooperation days only ->", math.ceil(coop), "; floor of total ->", math.floor(total))
print("ANSWER:", m[0])
