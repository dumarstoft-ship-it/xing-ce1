from fractions import Fraction as F
from itertools import product

print("=== G3-11 ===")
# T total days, x live days: eggs (T-x)/20 + 2x/20 = 1, peaches (T-x)/25 + 3x/25 = 1
for T in range(1, 30):
    for x in range(0, T + 1):
        if F(T - x, 20) + F(2 * x, 20) == 1 and F(T - x, 25) + F(3 * x, 25) == 1:
            print("T", T, "x", x)
print()

print("=== G3-12 ===")
for n in range(1, 200):
    if n % 2: continue
    g = [n - 10, n + 1, F(n, 2), 2 * n]
    if min(g) <= 0: continue
    if sum(g) + 2 == 4 * n and len(set(g)) == 4:
        print("n", n, "orig", g, "max-min", max(g) - min(g))
print()

print("=== G3-13 ===")
for N in range(50, 60):
    if N % 13 == 0:
        M = (N + 4) // 2; W = N - M
        print("N", N, "men", M, "women", W, "25% men", F(M, 4))
        for w in range(0, W + 1):
            cond1 = w <= 5            # any 6 contain a man  <=> women <= 5
            cond2 = w >= 4 + 1        # any distribution to 4 sites has a site with >=2 women
            if cond1 and cond2:
                print("  women", w, "total", F(M, 4) + w)
print()

print("=== G3-14 ===")
for k in [F(1), F(2), F(1, 2), F(3, 2)]:
    t1, t2, t3 = 3 * k, 4 * k, 5
    # 400 + 2d = 80 (7k+5)
    d = (80 * (t1 + t2 + t3) - 400) / 2
    print("k", k, "d2=d3", d, "v2", d / t2, "v3", d / t3, "v1", F(400) / t1)
print()

print("=== G3-15 ===")
# unit labor 3c, other c; after 1.5c, 0.9c; output Q -> 2Q; after: 2Q*1.5c - 2Q*0.9c = 3.6
cQ = F(36, 10) / (2 * F(3, 2) - 2 * F(9, 10))
save_unit = (3 + 1) - (F(3, 2) + F(9, 10))  # in units of c
per_day_new = save_unit * 2 * cQ
per_day_old = save_unit * cQ
print("cQ", cQ, "saving/day on new output", per_day_new, "days", F(3456) / per_day_new,
      "| on old output", per_day_old, "days", F(3456) / per_day_old)
print()

print("=== G3-16 ===")
first_ml = F(75 * 5, 15)
done_by_915 = 300 - 235
rate2 = (done_by_915 - first_ml) / 10  # ml/min
rem_min = F(235) / rate2
print("first 5 min ml", first_ml, "rate2 ml/min", rate2, "drops/min", rate2 * 15, "remaining min", rem_min)
total_sec = 15 * 60 + rem_min * 60
h = 9 + int(total_sec // 3600); m = int((total_sec % 3600) // 60); s = total_sec % 60
print("finish %d:%02d:%s" % (h, m, s))
print()

print("=== G3-17 ===")
# simulate with small steps (exact piecewise)
level = F(20)
t_full = (100 - level) / 20
print("full at", t_full)
level = F(100)  # at t=5
t_empty = 5 + level / (25 - 20)
print("empty at", t_empty, "| no-overflow trap:", 5 + F(20 + 100) / 5)
print()

print("=== G3-18 ===")
res = []
for x in range(1, 16):
    res.append((max(F(60, x), F(96, 16 - x)), x))
res.sort()
print(res[:3])
print()

print("=== G3-19 ===")
# 60 + 30(t-3) = 25 t
t = F(30, 5)
print("t", t, "task", 25 * t, 60 + 30 * (t - 3))
print()

print("=== G3-20 ===")
total = 44
m3 = 120 - 2 * total
print("machine3 worked", m3, "downtime", total - m3)
print()

print("=== G3-21 ===")
a = F(90, 12) + F(90, 18)
b = F(180, 30) * 2
print(a, b, a - b)
print()

print("=== G3-22 ===")
# total 72: 甲 4/day, 乙 3/day
print("strict (exact finish at end of whole days):")
sols = []
for x in range(1, 20):
    for y in range(1, 30):
        if 7 * x + 3 * y == 72 and x + y <= 19:
            sols.append((x, y, x + y))
print(sols, "min x =", min(s[0] for s in sols))
print("lenient (乙 counts whole days, may finish within last day):")
sols2 = []
for x in range(1, 20):
    for y in range(0, 30):
        if 7 * x + 3 * y >= 72 and x + y <= 19 and 7 * x < 72:
            # also need actual end time: x + (72-7x)/3 <= 19
            sols2.append((x, y, x + y, x + F(72 - 7 * x, 3)))
print("min x =", min(s[0] for s in sols2), [s for s in sols2 if s[0] == min(t[0] for t in sols2)][:3])
print("x=3 strict needs y=17 total", 3 + 17)
