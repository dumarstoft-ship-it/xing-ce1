from fractions import Fraction as F
from scipy.optimize import linprog
import math

print("=== G2-12 ===")
# vars: xJ (Jia processing hrs), iJ (Jia inspect hrs), xY, iY, T
# min T s.t. 12xJ+8xY>=96 ; 24iJ+40iY>=120 ; xJ+iJ<=T ; xY+iY<=T
c = [0, 0, 0, 0, 1]
A = [[-12, 0, -8, 0, 0], [0, -24, 0, -40, 0], [1, 1, 0, 0, -1], [0, 0, 1, 1, -1]]
b = [-96, -120, 0, 0]
r = linprog(c, A_ub=A, b_ub=b, bounds=[(0, None)] * 5)
print(r.x, r.fun)

print("=== G2-13 ===")
# j + y = 50 ; 1.2j + 0.9y = 54
j = (F(54) - F(9, 10) * 50) / (F(6, 5) - F(9, 10))
y = 50 - j
print("j", j, "y", y, "remaining hours", (360 - 2 * j) / (j + y))

print("=== G2-14 ===")
def finish(rest):
    work = F(0); day = 0
    total = F(60)
    while True:
        day += 1
        yi_works = (not rest) or (day % 5 != 0)
        rate = 3 + (2 if yi_works else 0)
        if work + rate >= total:
            return day - 1 + (total - work) / rate
        work += rate
a = finish(True); b0 = finish(False)
print("with rest", a, "no rest", b0, "diff", a - b0)

print("=== G2-15 ===")
# j + y = 60 ; 4j + 5*1.5j + 9y = 600
j = (F(600) - 9 * 60) / (4 + F(15, 2) - 9)
print("j", j)

print("=== G2-16 ===")
S = 15 * 30 - 15 * 12
stock = S + 5 * 12 - 5 * 30
stock += 5 * 18 - 5 * 30
x = F(stock + 5 * 18 - 5 * 30, 5)
print("S", S, "stock after day10", stock, "x", x)
# alt: increase applies days 6-15
stock5 = S + 5 * 12 - 5 * 30
print("alt (10 days) x", F(stock5 + 10 * 18 - 10 * 30, 10))

print("=== G2-17 ===")
dt = F(1, 100)
t = F(0); v = F(0)
while True:
    inflow = 9 if t < 10 else 0
    outflow = 6 if (t >= 4 and v > 0) else 0
    v = min(F(120), v + (inflow - outflow) * dt)
    t += dt
    if t > 10 and v <= 0:
        break
print("empty at", t)

print("=== G2-18 ===")
t = 0
for i in range(1, 44):
    t += 2
    if i % 6 == 0 and i < 43:
        t += 3
print(t)

print("=== G2-19 ===")
def docs(rate, work, rest, H):
    tot = 0
    for h in range(H):
        if h % (work + rest) < work:
            tot += rate
    return tot
print(docs(5, 3, 1, 10), docs(4, 2, 1, 10), docs(5, 3, 1, 10) - docs(4, 2, 1, 10))

print("=== G2-20 ===")
for n in range(1, 20):
    s = sum(4 + 2 * (k - 1) for k in range(1, n + 1))
    if s == 180:
        print("n", n)

print("=== G2-21 ===")
cum = 0
for d in range(1, 30):
    j = 10 if (d - 1) % 3 < 2 else 0
    y = 10 if (d - 1) % 4 < 3 else 0
    cum += j + y
    if cum >= 190:
        print("day", d, "cum", cum)
        break

print("=== G2-22 ===")
# machine 1 completion times
m1 = []
t = 0
while len(m1) < 60:
    for k in range(10):
        t += 1
        m1.append(t)
    t += 5
m2 = [2 * k for k in range(1, 60)]
allc = sorted(m1 + m2)
print("30th completion", allc[29], "first 32", allc[:32])

print("=== G2-23 ===")
cum = 0
for d in range(1, 20):
    cum += 12 + 4 + 2 * (d - 1)
    if cum >= 150:
        print("day", d, cum)
        break

print("=== G2-24 ===")
total = 24 * 15
cum = 0
for d in range(1, 60):
    if d <= 5:
        n = 24
    else:
        n = max(8, 20 - 4 * ((d - 6) // 2))
    cum += n
    if cum >= total:
        print("day", d, "cum", cum, "people on last day", n)
        break
