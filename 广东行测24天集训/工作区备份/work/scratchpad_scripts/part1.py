from fractions import Fraction as F
from itertools import product, combinations
from scipy.optimize import linprog
import math

print("=== G3-01: two machines, A/B parts, 40 sets ===")
# vars: a1 (甲 on A), b1 (甲 on B), a2 (乙 on A), b2 (乙 on B), T ; minimize T
# 8a1+4a2>=40 ; 4b1+6b2>=40 ; a1+b1<=T ; a2+b2<=T
c = [0, 0, 0, 0, 1]
A_ub = [[-8, 0, -4, 0, 0], [0, -4, 0, -6, 0], [1, 1, 0, 0, -1], [0, 0, 1, 1, -1]]
b_ub = [-40, -40, 0, 0]
r = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None)] * 5)
print("LP min T =", r.fun, r.x)
# integer-part check: at T=6, 甲 5h A (40A) + 1h B (4B), 乙 6h B (36B)
print("check T=6:", 8 * 5, 4 * 1 + 6 * 6)
# also check discrete parts: finished parts must be integers; search on grid of 1/60 h
best = None
for tA1_min in range(0, 60 * 8 + 1):
    pass
print()

print("=== G3-02: trucks ===")
def delivered(t):
    n1 = 0 if t < 30 else (t - 30) // 60 + 1
    n2 = 0 if t < 20 else (t - 20) // 40 + 1
    return n1, n2, 8 * n1 + 5 * n2
for t in range(0, 400):
    n1, n2, tot = delivered(t)
    if tot >= 67:
        print("first t with capacity>=67:", t, n1, n2, tot)
        break
for t in [210, 220, 230, 250, 259, 260, 270]:
    print(t, delivered(t))
print()

print("=== G3-03: two jobs 30, 42; speeds 2, 1; preemptive ===")
# lower bound and explicit schedule
LB = max(F(72, 3), F(42, 2))
print("LB =", LB)
# schedule: 0-18 甲 on J42 (36), 乙 on J30 (18); 18-24 甲 on J30 (12), 乙 on J42 (6)
print("J42:", 2 * 18 + 1 * 6, "J30:", 1 * 18 + 2 * 6)
# also LP formulation via interval-free reasoning: Q2|pmtn|Cmax = max(p1/s1, (p1+p2)/(s1+s2))
print()

print("=== G3-04: tasks 2,3,5,7,9 (乙 hours); 甲 twice as fast; 9 must be 甲 ===")
tasks = [2, 3, 5, 7]
best = None
res = []
for assign in product([0, 1], repeat=4):  # 1 -> 乙
    yi = sum(t for t, a in zip(tasks, assign) if a == 1)
    jia = F(9, 2) + sum(F(t, 2) for t, a in zip(tasks, assign) if a == 0)
    mk = max(F(yi), jia)
    res.append((mk, assign))
res.sort()
print("min makespan:", res[0][0], [r for r in res if r[0] == res[0][0]])
print()

print("=== G3-05 ===")
W = F(1)
r1, r2 = F(3), F(2)
W = F(15)  # pick
t_jia = (F(2, 5) * W) / r1
done = F(2, 5) * W + r2 * t_jia
rest = W - done
T = t_jia + rest / r2
T0 = W / (r1 + r2)
print("reading 甲 himself 2/5: T=", T, "T0=", T0, "increase=", (T - T0) / T0)
# alt: together complete 2/5
t_tog = F(2, 5) * W / (r1 + r2)
T_alt = t_tog + F(3, 5) * W / r2
print("reading together 2/5: increase=", (T_alt - T0) / T0)
print()

print("=== G3-06: transport ===")
best = None
for x in range(0, 51):  # A->甲 (integer tons; LP is linear anyway)
    a_yi = 50 - x
    b_jia = 60 - x
    b_yi = 70 - b_jia
    if a_yi < 0 or b_jia < 0 or b_yi < 0 or a_yi > 30:
        continue
    cost = 15 * x + 13 * a_yi + 16 * b_jia + F(29, 2) * b_yi
    if best is None or cost < best[0]:
        best = (cost, x, a_yi, b_jia, b_yi)
print("min cost (with A->乙<=30):", best)
best2 = None
for x in range(0, 51):
    a_yi = 50 - x; b_jia = 60 - x; b_yi = 70 - b_jia
    if a_yi < 0 or b_jia < 0 or b_yi < 0: continue
    cost = 15 * x + 13 * a_yi + 16 * b_jia + F(29, 2) * b_yi
    if best2 is None or cost < best2[0]:
        best2 = (cost, x)
print("min cost (no cap):", best2)
# continuous LP check
r = linprog([15, 13, 16, 14.5], A_eq=[[1, 1, 0, 0], [0, 0, 1, 1], [1, 0, 1, 0], [0, 1, 0, 1]],
            b_eq=[50, 70, 60, 60], bounds=[(0, None), (0, 30), (0, None), (0, None)])
print("LP:", r.fun, r.x)
print()

print("=== G3-07 ===")
best = None
for x in range(10, 41):
    for y in range(0, 101):
        if 2 * x + y <= 80 and x + 2 * y <= 100:
            if best is None or x + y > best[0]:
                best = (x + y, [(x, y)])
            elif x + y == best[0]:
                best[1].append((x, y))
print(best)
print()

print("=== G3-08 ===")
# time per initial item = 1.5 min; rework 0.75 min; 420 min
best = 0
for batches in range(0, 100):
    t = batches * (10 * F(3, 2) + F(3, 4))
    if t <= 420:
        best = batches
print("batches", best, "items", best * 10, "time", best * (10 * F(3, 2) + F(3, 4)))
print("continuous:", F(420) / (F(3, 2) + F(3, 40)))
print()

print("=== G3-09 ===")
best = None
for n in range(0, 10):
    for r in range(0, n + 1):
        good = 48 * n + 12 * r
        t = 3 * n + r
        if good >= 200:
            if best is None or t < best[0]:
                best = (t, n, r, good)
print(best)
print()

print("=== G3-10 ===")
items = [('A', i, 6) for i in range(3)] + [('B', i, 4) for i in range(4)] + [('C', i, 3) for i in range(5)]
maxk = 0
cnt = {}
for k in range(1, 13):
    c = 0
    for comb in combinations(items, k):
        if sum(x[2] for x in comb) <= 30:
            c += 1
    cnt[k] = c
    if c > 0:
        maxk = k
print("max count:", maxk, "num subsets:", cnt[maxk], cnt)
