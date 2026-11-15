# -*- coding: utf-8 -*-
"""Blind solve for Q40 (screws & nuts, two workshops). Exact arithmetic with Fraction."""
from fractions import Fraction as F
from itertools import combinations
import math

# rates per hour
A_N, A_M = 40, 50   # A: 40 screws (钉) OR 50 nuts (帽)
B_N, B_M = 30, 60   # B: 30 screws OR 60 nuts

# Step 1: batch size.  N/B_N - N/A_N = 20
N = F(20) / (F(1, B_N) - F(1, A_N))
print("N (screws = nuts) =", N)
assert N == 2400
N = int(N)

# Step 2: exact LP by vertex enumeration in (a, b, T)
#   a = hours A spends on screws (rest T-a on nuts), b = hours B spends on screws.
#   constraints written as  c . (a,b,T) <= d
cons = [
    ((-1, 0, 0), 0),                 # a >= 0
    ((0, -1, 0), 0),                 # b >= 0
    ((1, 0, -1), 0),                 # a <= T
    ((0, 1, -1), 0),                 # b <= T
    ((-A_N, -B_N, 0), -N),           # 40a + 30b >= N  (screws)
    ((A_M, B_M, -(A_M + B_M)), -N),  # 50(T-a) + 60(T-b) >= N  (nuts)
    ((0, 0, 1), 1000),               # bounding box
]

def solve3(rows):
    # Cramer's rule with Fractions
    M = [[F(x) for x in r[0]] for r in rows]
    d = [F(r[1]) for r in rows]
    def det(m):
        return (m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])
                - m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])
                + m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]))
    D = det(M)
    if D == 0:
        return None
    sol = []
    for k in range(3):
        Mk = [row[:] for row in M]
        for i in range(3):
            Mk[i][k] = d[i]
        sol.append(det(Mk) / D)
    return sol

best = None
for trio in combinations(cons, 3):
    s = solve3(trio)
    if s is None:
        continue
    if all(sum(F(c)*x for c, x in zip(row, s)) <= d for row, d in cons):
        if best is None or s[2] < best[2]:
            best = s
a, b, T = best
print("LP optimum: T* =", T, "=", float(T), "h;  A on screws a =", a, " B on screws b =", b,
      "(B on nuts", T - b, "h)")
print("  screws =", A_N*a + B_N*b, " nuts =", A_M*(T-a) + B_M*(T-b))
print("  ceil(T*) =", math.ceil(T))

# Step 3: integer-hour schedules (each workshop makes only one product in each whole hour)
#   Work in units of 1/k hour, integers only: T, a, b are counts of 1/k-hour slots.
def min_T_grid(k=1, Tmax_hours=200):
    for Tu in range(1, Tmax_hours * k + 1):
        for au in range(Tu + 1):
            # screws: 40*au + 30*bu >= N*k ; nuts: 50*(Tu-au) + 60*(Tu-bu) >= N*k
            need = N * k - A_N * au
            b_lo = 0 if need <= 0 else -(-need // B_N)          # ceil
            room = A_M * (Tu - au) + B_M * Tu - N * k           # 60*bu <= room
            if room < 0:
                continue
            b_hi = min(Tu, room // B_M)
            if b_lo <= b_hi:
                return F(Tu, k), F(au, k), F(b_lo, k)
    return None

Ti, ai, bi = min_T_grid(1)
print("Integer-hour allocation: min T =", Ti, " (A screws", ai, "h, B screws", bi, "h, B nuts", Ti - bi, "h)")
for TT in (51, 52):
    # exact max screws in T hours subject to nuts >= N (greedy by comparative advantage, continuous)
    # B makes nuts first (60/h, loses 2 screws-equivalent... ) -> B needs N/60 = 40 h of nuts
    bn = F(N, B_M)
    screws = A_N * TT + B_N * (TT - bn)
    print(f"  T={TT}: max screws with all {N} nuts made = {screws} -> feasible={screws >= N}")
for k in (2, 3, 7, 10):
    Tk, _, _ = min_T_grid(k)
    print(f"  allocation in 1/{k}-hour units: min T = {Tk} = {float(Tk):.4f} -> billed {math.ceil(Tk)} h")

# Step 4: alternative / wrong readings
print("\nAlternative readings / error paths:")
print("  floor instead of ceil:", math.floor(T))
print("  no switching (A screws only, B nuts only): max(", F(N, A_N), ",", F(N, B_M), ") =", max(F(N, A_N), F(N, B_M)))
print("  no switching, reversed (A nuts, B screws): max(", F(N, A_M), ",", F(N, B_N), ") =", max(F(N, A_M), F(N, B_N)))
seq = F(N, A_N + B_N) + F(N, A_M + B_M)
print("  both do screws together then nuts together:", seq, "=", float(seq), "-> ceil", math.ceil(seq))
setA = 1 / (F(1, A_N) + F(1, A_M)); setB = 1 / (F(1, B_N) + F(1, B_M))
ss = N / (setA + setB)
print("  each workshop makes complete sets itself:", ss, "=", float(ss), "-> ceil", math.ceil(ss))
# reversed specialization with switching: A nuts first then helps screws
tA = F(N, A_M)              # A finishes nuts at 48h
rem = N - B_N * tA          # screws remaining
rev = tA + rem / (A_N + B_N)
print("  reversed specialization (A nuts->then screws, B screws):", rev, "=", float(rev), "-> ceil", math.ceil(rev))
print("  total workshop-hours (sum, not elapsed):", F(N, A_N) + F(N, B_M))
# rounding each phase separately for the correct plan
ph1 = F(N, B_M); ph2 = (N - A_N*ph1) / (A_N + B_N)
print("  correct plan phase-wise: phase1", ph1, "h + phase2", ph2, "=", float(ph2), "-> 40 +", math.ceil(ph2), "=", ph1 + math.ceil(ph2))
