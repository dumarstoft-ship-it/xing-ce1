"""Q31: 6, 1, 13, 15, 41, ( )   options A68 B69 C70 D71
Fit the general linear recursion a(n+2) = p*a(n+1) + q*a(n) + r to the three known
transitions (3 equations, 3 unknowns), check the fit is unique and integral, then
predict the next term and match it against the options."""
from fractions import Fraction as F

seq = [6, 1, 13, 15, 41]
opts = {"A": 68, "B": 69, "C": 70, "D": 71}

rows = [[F(seq[i + 1]), F(seq[i]), F(1), F(seq[i + 2])] for i in range(3)]
n = 3
for c in range(n):
    piv = next(r for r in range(c, n) if rows[r][c] != 0)
    rows[c], rows[piv] = rows[piv], rows[c]
    for r in range(n):
        if r != c and rows[r][c] != 0:
            f = rows[r][c] / rows[c][c]
            rows[r] = [x - f * y for x, y in zip(rows[r], rows[c])]
p, q, r = (rows[i][3] / rows[i][i] for i in range(3))
print("unique linear fit: p =", p, " q =", q, " r =", r)
assert (p, q, r) == (1, 2, 0)

for i in range(3):
    print(f"{seq[i+1]} + 2*{seq[i]} = {seq[i+1] + 2*seq[i]}  (actual {seq[i+2]})")
pred = seq[-1] + 2 * seq[-2]
print("predicted: 41 + 2*15 =", pred)
matches = [k for k, v in opts.items() if v == pred]
assert matches == ["D"], matches

# No other option fits a recursion of the same shape with the same coefficients.
for k, v in opts.items():
    print(k, v, "fits a(n)=a(n-1)+2a(n-2)?", v == pred)
print("ANSWER:", matches[0])
