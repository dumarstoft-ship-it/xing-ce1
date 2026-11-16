"""Q39: 600 parts, Wang+Liu 30 h -> combined 20/h. Parts +25% -> 750 in the same 30 h -> 25/h.
Wang's efficiency +12.5% (x9/8), Liu's +1/3 (x4/3). Find |Wang - Liu| originally."""
from fractions import Fraction as F
total = F(600) / 30
new_total = F(600) * F(5, 4) / 30
sols = []
# exact solve
# w + l = 20 ; 9/8 w + 4/3 l = 25
l = (new_total - F(9, 8) * total) / (F(4, 3) - F(9, 8))
w = total - l
print("exact: Wang =", w, "Liu =", l, "check new:", F(9, 8) * w + F(4, 3) * l)
# enumeration over rational efficiencies with denominator up to 24 (to be safe)
for den in range(1, 25):
    for wn in range(0, 20 * den + 1):
        ww = F(wn, den)
        ll = total - ww
        if F(9, 8) * ww + F(4, 3) * ll == new_total:
            sols.append((ww, ll))
sols = sorted(set(sols))
print("all solutions found by enumeration:", sols)
assert sols == [(F(8), F(12))]
diff = abs(w - l)
opts = {"A": 7, "B": 6, "C": 5, "D": 4}
m = [k for k, v in opts.items() if v == diff]
assert m == ["D"], m
print("difference =", diff, "ANSWER:", m[0])
