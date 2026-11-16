"""Q35 table (rows: col1, col2, col3):
   2  2  6
   3  6 21
   7  5 42
   5 18  ?        options A95 B96 C97 D98
Main rule: col3 = col1 x (col2 + 1).
Robustness: search small integer formulas c = p*a*b + q*a + r*b + s and c = p*a^2 + q*b^2 + r*a + s*b
(|coef| <= 3) that fit all three known rows, and list what they predict for row 4."""
from itertools import product
from collections import Counter

rows = [(2, 2, 6), (3, 6, 21), (7, 5, 42)]
last = (5, 18)
opts = {"A": 95, "B": 96, "C": 97, "D": 98}

for a, b, c in rows:
    print(f"{a} x ({b}+1) = {a*(b+1)}  (actual {c})")
    assert a * (b + 1) == c
pred = last[0] * (last[1] + 1)
print("row 4:", f"5 x (18+1) = {pred}")
matches = [k for k, v in opts.items() if v == pred]
assert matches == ["A"], matches

R = range(-3, 4)
fam1 = Counter()
fits1 = []
for p, q, r, s in product(R, R, R, R):
    if all(p * a * b + q * a + r * b + s == c for a, b, c in rows):
        a, b = last
        v = p * a * b + q * a + r * b + s
        fam1[v] += 1
        fits1.append((p, q, r, s, v))
print("family c = p*ab + q*a + r*b + s, |coef|<=3, fits:", fits1)

fam2 = []
for p, q, r, s in product(R, R, R, R):
    if all(p * a * a + q * b * b + r * a + s * b == c for a, b, c in rows):
        a, b = last
        fam2.append((p, q, r, s, p * a * a + q * b * b + r * a + s * b))
print("family c = p*a^2 + q*b^2 + r*a + s*b, |coef|<=3, fits:", fam2)

hits = {k: v for k, v in opts.items() if v in fam1 or any(f[-1] == v for f in fam2)}
print("options reachable by any small formula in these families:", hits)
assert hits == {"A": 95}
print("ANSWER:", matches[0])
