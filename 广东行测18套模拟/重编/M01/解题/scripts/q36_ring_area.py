"""Q36: circular bed circumference 62.8 m, a 1 m wide path around the outside, pi = 3.14."""
from fractions import Fraction as F
pi = F(314, 100)
C = F(628, 10)
r = C / (2 * pi)
R = r + 1
area = pi * (R * R - r * r)
print("r =", r, " R =", R, " area = 3.14*(11^2-10^2) =", float(area))
opts = {"A": F(6594, 100), "B": F(7065, 100), "C": F(7536, 100), "D": F(8038, 100)}
# common traps: path inside the bed (r-1 = 9): 3.14*(100-81)
print("trap (path inside):", float(pi * (r * r - (r - 1) ** 2)), " trap (outer circle area 11^2*pi):", float(pi * R * R))
m = [k for k, v in opts.items() if v == area]
assert m == ["A"], m
print("ANSWER:", m[0])
