from fractions import Fraction as F
from itertools import product
from scipy.optimize import linprog
import math

print("=== G3-23 ===")
for s in range(0, 21):
    a = 20 - s
    if a <= 2 * s and 5 * s + 3 * a >= 78:
        print("min skilled", s, "apprentices", a, "output", 5 * s + 3 * a)
        break
print()

print("=== G3-24: flow shop with batch transfer of 5 ===")
t_jia = 0
t_yi = 0
for b in range(4):
    t_jia += 5 * 2  # batch done
    start = max(t_jia, t_yi)
    t_yi = start + 5 * 3
    print("batch", b + 1, "甲 done", t_jia, "乙 start", start, "乙 done", t_yi)
print("makespan", t_yi)
print()

print("=== G3-25 ===")
yi = 15 * 4
jia = 130 - yi
m = 2 - F(jia - 40, 25)
print("甲 total", jia, "meeting hours", m, "minutes", m * 60)
print()

print("=== G3-26 ===")
def cnt(t):
    a = max(0, (t - 5) // 2) if t >= 5 else 0
    b = max(0, (t - 7) // 3) if t >= 7 else 0
    return a, b, a + b
for t in range(0, 200):
    if cnt(t)[2] >= 53:
        print("first t", t, cnt(t), "t-1:", cnt(t - 1))
        break
print()

print("=== G3-27 ===")
def deliv(t):
    return 15 * (t // 18) + 10 * (t // 12)
for t in range(0, 200):
    if deliv(t) >= 75:
        print("first t", t, deliv(t), "prev event 48:", deliv(48))
        break
print()

print("=== G3-28 ===")
done = 0
d = 0
while done < 880:
    d += 1
    done += 80 if d <= 5 else 80 + 2 * 10 * F(4, 5)
print("day", d, "done", done)
print()

print("=== G3-29 ===")
# simulate per-hour exact
level = F(0); t = F(0)
found = None
while found is None:
    # fill phase 2h at 8
    if level + 16 >= 30:
        found = t + (30 - level) / 8
        break
    level += 16; t += 2
    level -= 5; t += 1
print("full at", found)
print()

print("=== G3-30 ===")
need = 0
for t100 in range(0, 1001):  # check t in steps of 0.01 h, just before deliveries too
    t = F(t100, 100)
    deliveries = sum(1 for d in (3, 6, 9) if d < t)  # just-before: strict (worst case)
    need = max(need, 5 * t - 10 * deliveries)
print("min initial stock", need)
print()

print("=== G3-31: LP ===")
# vars: a1,a2,a3 (甲 X,Y,Z), b1,b2,b3 (乙), T
c = [0] * 6 + [1]
A_ub = [
    [-6, 0, 0, -3, 0, 0, 0],
    [0, -4, 0, 0, -4, 0, 0],
    [0, 0, -2, 0, 0, -6, 0],
    [1, 1, 1, 0, 0, 0, -1],
    [0, 0, 0, 1, 1, 1, -1],
]
b_ub = [-60, -80, -60, 0, 0]
r = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None)] * 7)
print("LP min T", r.fun, r.x)
print()

print("=== G3-32: unbounded knapsack max boxes ===")
packs = [(1, 10), (5, 40), (10, 70), (20, 120)]
def maxbox(B):
    best = [0] * (B + 1)
    for b in range(B + 1):
        for n, p in packs:
            if p <= b:
                best[b] = max(best[b], best[b - p] + n)
    return best[B]
a, b, ab = maxbox(575), maxbox(639), maxbox(575 + 639)
print("甲", a, "乙", b, "sum", a + b, "combined", ab, "diff", ab - (a + b))
print()

print("=== G3-33 ===")
best = []
for na in range(0, 11):
    for nb in range(0, 11 - na):
        if 8 * na + 12 * nb >= 100:
            cost = 100 * na + 170 * nb + (200 if na else 0) + (100 if nb else 0)
            best.append((cost, na, nb))
best.sort()
print(best[:5])
print()

print("=== G3-34 ===")
# 8a+8b=300 ; 2*0.8a + 3*0.8b = 80
import numpy as np
sol = np.linalg.solve([[8, 8], [1.6, 2.4]], [300, 80])
a_, b_ = F(sol[0]).limit_denominator(100), F(sol[1]).limit_denominator(100)
daily = 300 + 4 * F(4, 5) * a_
print("a", a_, "b", b_, "new daily", daily, "days", F(1440) / daily, "ceil", math.ceil(F(1440) / daily))
print()

print("=== G3-35: two-phase with transfer ===")
# units: total 60, front 30, back 30; 甲3/day, 乙2/day, 丙1/day
def end_time(L):
    # 甲 works front on [0, min(L, Ffront)], 乙 works front from 0 until front done
    # front completion: if 甲 leaves at L before front completes: 3L + 2Ff = 30
    if 5 * L >= 30:
        Ff = F(30, 5)
        L_eff = Ff  # 甲 leaves at front end
    else:
        Ff = (30 - 3 * L) / 2
        L_eff = L
    arrive = L_eff + 2
    # back from Ff: 丙 1/day from Ff, 甲 3/day from max(arrive, Ff)
    s = max(arrive, Ff)
    # work by 丙 from Ff to s
    w = s - Ff
    if w >= 30:
        return Ff + 30, Ff, arrive
    E = s + (30 - w) / 4
    return E, Ff, arrive
best = None
for k in range(0, 6001):
    L = F(k, 1000)
    E, Ff, arr = end_time(L)
    if best is None or E < best[0]:
        best = (E, L, Ff, arr)
print("best E", best[0], float(best[0]), "leave", best[1], "front end", best[2], "甲 arrives", best[3])
print("no early leave (L=6):", end_time(F(6)))
# 甲 never in front, only back (no transfer needed)
print("甲 only back:", F(15) + F(30, 4))
