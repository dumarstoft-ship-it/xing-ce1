from fractions import Fraction as F
from itertools import permutations, product, combinations
import math

print("=== G2-01 ===")
# 4 tasks, 2 identical machines, non-preemptive, minimize sum of completion times
tasks = [2, 4, 7, 9]
best = None
vals = set()
for assign in product([0, 1], repeat=4):
    for perm in permutations(range(4)):
        t = [0, 0]
        tot = 0
        for i in perm:
            m = assign[i]
            t[m] += tasks[i]
            tot += t[m]
        vals.add(tot)
        if best is None or tot < best[0]:
            best = (tot, assign, perm)
print("min sum completion", best)
print("achievable values sorted", sorted(vals)[:10])
# alternative reading: waiting = time before service starts
best2 = None
for assign in product([0, 1], repeat=4):
    for perm in permutations(range(4)):
        t = [0, 0]
        tot = 0
        for i in perm:
            m = assign[i]
            tot += t[m]
            t[m] += tasks[i]
        if best2 is None or tot < best2:
            best2 = tot
print("alt (wait before start) min", best2)

print("=== G2-02 ===")
rev = [2, 4, 6]
sysT = [12, 8, 4]
# reading 1: application i -> its own system time sysT[i]
res = []
for perm in permutations(range(3)):
    t = 0
    fin = []
    for i in perm:
        t += rev[i]
        fin.append(t + sysT[i])
    res.append((max(fin), perm))
print("reading1 (tail fixed per application):", sorted(res))
# reading 2: any application can go to any system (system j has time sysT[j])
res2 = []
for perm in permutations(range(3)):
    for sp in permutations(range(3)):
        t = 0
        fin = []
        for k, i in enumerate(perm):
            t += rev[i]
            fin.append(t + sysT[sp[k]])
        res2.append(max(fin))
print("reading2 min:", min(res2))

print("=== G2-03 ===")
ja, yi = F(1, 12), F(1, 18)
both = F(4, 5) * (ja + yi)
print("combined rate", both)
T = F(21, 2)
# t*ja + (T - t)*both = 1
t = (1 - T * both) / (ja - both)
print("max solo t", t, float(t))
for opt in [F(9, 2), F(15, 2), F(3), F(6)]:
    rem = 1 - opt * ja
    total = opt + rem / both
    print(" option", opt, "total time", total, float(total))

print("=== G2-04 ===")
best = []
for A in range(0, 7):
    for B in range(0, 7):
        a = min(A, 5)
        b = min(B, 5)
        if F(a, 6) + F(b, 9) >= 1:
            best.append((200 * A + 120 * B, A, B))
best.sort()
print("cheapest ceilings:", best[:6])
# fine grid sanity check
mn = None
for ai in range(0, 501):
    a = F(ai, 100)
    b = (1 - a / 6) * 9
    if b < 0 or b > 5:
        continue
    c = 200 * math.ceil(a) + 120 * math.ceil(b)
    if mn is None or c < mn[0]:
        mn = (c, a, b)
print("grid min", mn)
# ignore 5h limit
best_nolimit = []
for A in range(0, 7):
    for B in range(0, 10):
        if F(A, 6) + F(B, 9) >= 1:
            best_nolimit.append((200 * A + 120 * B, A, B))
print("no-deadline min", sorted(best_nolimit)[:3])

print("=== G2-05 ===")
# 2(8a+5b) + (6a+5b) + 3(6a+7b) = 6(8a+5b)
# coefficient: a: 16+6+18 - 48 = -8 ; b: 10+5+21-30 = 6 -> 6b = 8a
a = F(3)
b = F(4)
assert 2*(8*a+5*b) + (6*a+5*b) + 3*(6*a+7*b) == 6*(8*a+5*b)
W = 6 * (8 * a + 5 * b)
rem = W - 2 * (8 * a + 5 * b)
r = rem / (4 * (6 * a + 5 * b)) - 1
print("W", W, "rem", rem, "r", r)

print("=== G2-06 ===")
per_hour = 60 // 6 + 60 // 5 + 60 // 4
print("3 people per hour", per_hour, "hours", F(259, per_hour))
H = 7
robot = 60 // 2 * H
robot_auto = F(4, 5) * robot
human = (60 // 5 + 60 // 4) * H
print("robot processed", robot, "auto", robot_auto, "human", human, "total", robot_auto + human)

print("=== G2-07 ===")
z = F(4, 100) / 1  # Bing per day: 40% in 10 days
z = F(40, 100) / 10
for name, (p, q, s) in {"A": (5, 4, 6), "B": (6, 4, 5), "C": (10, 15, 12), "D": (12, 15, 10)}.items():
    k = z / s
    j, y = p * k, q * k
    print(name, "9y+6(j+y) =", 9 * y + 6 * (j + y))

print("=== G2-08 ===")
print(20 * 1 + 20 * 2 * F(6, 5) + 20 * 3 * F(3, 2))

print("=== G2-09 ===")
# m + n = 1/3 ; 2m + 5n = 1
n = (1 - 2 * F(1, 3)) / 3
m = F(1, 3) - n
print("m", m, "n", n, "M alone", 1 / m, "check", 2 * m + 5 * n)

print("=== G2-10 ===")
T = F(1)
dy, db = T / 32, T / 24
tY40 = 40 * dy
print("Bing done at that time", tY40 / db, "remaining", 40 - tY40 / db)

print("=== G2-11 ===")
# y=1, j=5/4 ; W = t_y
for ty in [16, 18, 20, 22]:
    W = F(ty)
    y = F(1); j = F(5, 4)
    help_time = 2 * W / (j + y)
    print(ty, "saving", W - help_time)
