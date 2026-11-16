"""Q33: 180, 56, 146, 174, 247, ( )  options A289 B334 C376 D412
Fit the general linear recursion a(n+2) = p*a(n+1) + q*a(n) + r to the
three known transitions (3 equations, 3 unknowns) and see what comes out."""
from fractions import Fraction as F

seq = [180, 56, 146, 174, 247]
opts = {"A": 289, "B": 334, "C": 376, "D": 412}

# Solve [a1 a0 1][p q r]^T = a2 for the three transitions by Gaussian elimination
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
assert (p, q, r) == (1, F(1, 2), 0)

for i in range(3):
    print(f"{seq[i+1]} + {seq[i]}/2 = {seq[i+1] + F(seq[i], 2)}  (actual {seq[i+2]})")
pred = seq[-1] + F(seq[-2], 2)
print("predicted: 247 + 174/2 =", pred)
matches = [k for k, v in opts.items() if v == pred]
assert matches == ["B"], matches
print("ANSWER:", matches[0])
