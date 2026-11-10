from fractions import Fraction as F
import itertools, random

def show(bid, *a):
    print(bid, *a)

# G1-01
a, b = F(1, 10), F(1, 15)
# a*T + b*(T - 5/3) = 1
T = (1 + b * F(5, 3)) / (a + b)
ja, yi = a * T, b * (T - F(5, 3))
total = F(300) / (ja - yi)
show('G1-01', 'T=', T, 'jia=', ja, 'yi=', yi, 'total=', total)

# G1-02
ja_d = F(10, 100) / 12
yi_d = F(15, 100) / 12
rem = 1 - F(25, 100)
need = rem - 30 * ja_d - 30 * yi_d * F(8, 10)
bing = need / 30
show('G1-02', 'bing/jia=', bing / ja_d)

# G1-03
ab, bc, ac = F(1, 6), F(1, 8), F(1, 12)
s = (ab + bc + ac) / 2
A, B, C = s - bc, s - ac, s - ab
show('G1-03', 'A,B,C=', A, B, C, 'time=', (1 - 4 * A) / s)

# G1-04 / G1-05
top3, bot3, all5 = F(1, 6), F(1, 12), F(1, 5)
a3 = top3 + bot3 - all5
a45 = bot3 - a3
a12 = top3 - a3
show('G1-04', 'a3=', a3, 'a4+a5=', a45, 'a1+a2=', a12, 'max days 2 lines doubled=', 1 / (2 * a45))
# feasibility check with random distinct values
ok = 0
for _ in range(20000):
    a2 = a3 + (a12 / 2 - a3) * F(random.randint(1, 999), 1000)
    a1 = a12 - a2
    a4 = a45 / 2 + (min(a3, a45) - a45 / 2) * F(random.randint(1, 999), 1000)
    a5 = a45 - a4
    v = [a1, a2, a3, a4, a5]
    if not (a1 > a2 > a3 > a4 > a5 > 0):
        continue
    sums3 = [sum(c) for c in itertools.combinations(v, 3)]
    sums2 = [2 * sum(c) for c in itertools.combinations(v, 2)]
    assert max(sums3) == top3 and min(sums3) == bot3 and sum(v) == all5
    assert 1 / min(sums2) == 15
    ok += 1
show('G1-04', 'random feasible instances checked:', ok)
show('G1-05', 'days=', 1 / (all5 + a3 / 2))

# G1-06 units 600: jia 3, yi 2
W = 600
done60 = 60 * 5
for R in range(60, 141):
    work = done60 + 3 * (140 - 60) + 3 * (140 - R)
    if work >= W:
        last = R
show('G1-06', 'latest return end of day', last)
# alternative reading: yi back to original when jia returns
for R in range(60, 141):
    work = done60 + 3 * (R - 60) + 5 * (140 - R)
    if work >= W:
        last2 = R
show('G1-06', '(alt reading yi reverts) latest', last2)

# G1-07
# 2a+9b=1, 6a+6b=1
import numpy as np
from sympy import symbols, solve, Rational
x, y = symbols('x y')
sol = solve([2 * x + 9 * y - 1, 6 * x + 6 * y - 1], [x, y])
a, b = sol[x], sol[y]
show('G1-07', 'a,b=', a, b, 'time=', 1 / (a * Rational(4, 3) + b))

# G1-08
a, b = F(1, 12), F(1, 18)
rem = 1 - 3 * (a + b)
t = rem / (a + b * F(3, 2))
show('G1-08', 'total hours', 3 + t)

# G1-09
need = F(75, 100) - 30 * ja_d - 24 * yi_d * F(8, 10)
bing = need / 24
show('G1-09', 'bing/jia=', bing / ja_d)

# G1-10
# 0.5a = 0.3(a+b) -> a:b
a, b = F(3), F(2)
assert F(1, 2) * a == F(3, 10) * (a + b)
s0 = a + b
s1 = a * F(5, 4) + b * F(3, 4)
# W/s0 - W/s1 = 2
Wt = 2 / (1 / s0 - 1 / s1)
show('G1-10', 'orig days', Wt / s0)

# G1-11
cum = 0
for h in range(1, 30):
    if h <= 2:
        cum += 120 * F(9, 10)
    else:
        cum += 100 * F(9, 10) + 100 * F(96, 100)
    if cum >= 1700:
        show('G1-11', 'hour', h, 'cum', cum)
        break

# G1-12
import datetime
d0 = datetime.date(2026, 7, 1)  # 2026-07-01 is Wednesday
assert d0.weekday() == 2
res = []
for start in range(1, 32):
    def cnt(end):
        c = 0
        for d in range(start, end + 1):
            if datetime.date(2026, 7, d).weekday() < 5:
                c += 1
        return c
    n28, n20 = cnt(28), cnt(20)
    if start <= 20 and 20 * n28 == 30 * n20 and n20 > 0:
        # also need last reading day exactly 28 / 20 (both weekdays)
        res.append((start, n20, n28))
show('G1-12', 'inclusive reading:', res)
res = []
for start in range(1, 32):
    def cnt(end):
        c = 0
        for d in range(start, end + 1):
            if datetime.date(2026, 7, d).weekday() < 5:
                c += 1
        return c
    n27, n19 = cnt(27), cnt(19)
    if start <= 19 and 20 * n27 == 30 * n19 and n19 > 0:
        res.append((start, n19, n27))
show('G1-12', 'exclusive reading (finish before 28/20):', res)

# G1-13
done = 3 * 12 + 2 * 6
show('G1-13', 'total', 5 + F(288 - done, 20))

# G1-14
for T in range(1, 100):
    if F(1, T + 6) + F(1, T + 24) == F(1, T):
        show('G1-14', 'T', T)

# G1-15
vals = set()
for x in range(4, 18):
    for y in range(4, 18):
        z = 17 - x - y
        if z >= 4:
            vals.add(max(x, y, z))
show('G1-15', sorted(vals), len(vals))

# G1-16
best = None
for x in range(4, 27):
    for y in range(4, 27):
        z = 26 - x - y
        if z >= 4:
            m = max(60 * x, 40 * y, 30 * z)
            if best is None or m < best[0]:
                best = (m, [(x, y, z)])
            elif m == best[0]:
                best[1].append((x, y, z))
show('G1-16', 'min minutes', best[0], 'allocs', best[1], 'continuous', F(26 * 60, 1) / F(9, 2) / 60 * 60)

# G1-17
jobs = [3, 4, 6, 7]
best = None
for mask in range(1, 15):
    S = [jobs[i] for i in range(4) if mask >> i & 1]
    R = [jobs[i] for i in range(4) if not mask >> i & 1]
    m = max(F(sum(S), 2), sum(R))
    if best is None or m < best[0]:
        best = (m, [(S, R)])
    elif m == best[0]:
        best[1].append((S, R))
show('G1-17', best)

# G1-18
best = None
for x in range(1, 20):
    m = max(F(90, x), F(140, 20 - x))
    if best is None or m < best[0]:
        best = (m, x)
show('G1-18', 'no transfer ever', best, float(best[0]))
# alt: finished group joins the other
best2 = None
for x in range(1, 20):
    t1, t2 = F(90, x), F(140, 20 - x)
    if t1 <= t2:
        done2 = (20 - x) * t1
        T = t1 + (140 - done2) / 20
    else:
        done1 = x * t2
        T = t2 + (90 - done1) / 20
    if best2 is None or T < best2[0]:
        best2 = (T, x)
show('G1-18', 'finished group may join other', best2)

# G1-19
total = 30 * 20
done = 30 * 4 + 20 * 4
for n in range(0, 50):
    if done + 12 * (20 + F(3, 4) * n) >= total:
        show('G1-19', 'n', n)
        break

# G1-20
ja = 3 * 4 + 2 * 6
yi = 2 * 4 + F(3, 2) * 6
show('G1-20', F(ja) / (ja + yi))

# G1-21
r = symbols('r')
rr = solve((Rational(3, 2) + r) * 50 - (2 + r) * 40, r)[0]
show('G1-21', 'loss', rr, 'S', (2 + rr) * 40)

# G1-22
rr = solve((2 + r) * 50 - (Rational(26, 10) + r) * 40, r)[0]
S = (2 + rr) * 50
rem = S - 20 * (2 + rr)
xx = rem / 20 - rr / 2
show('G1-22', 'loss', rr, 'S', S, 'rem', rem, 'x', xx)

# G1-23
# N + 40v = 120, N + 20v = 100
v = F(20, 20); N = 100 - 20 * v
q = N + 20 * v - 2 * 20
assert all(N + t * v - 2 * t > 0 for t in range(0, 20))
t2 = q / (3 - 2 * v)
show('G1-23', 'N', N, 'v', v, 'q20', q, 'total', 20 + t2)

# G1-24
V = symbols('V')
a_ = V / 60 + 5; b_ = V / 90 + 5
Vv = solve((a_ + b_ - 5) * 30 - V, V)[0]
show('G1-24', 'V', Vv, 'a', a_.subs(V, Vv), 'b', b_.subs(V, Vv))

# G1-25
def sim25(first):
    rates = [8, 6] if first == 'jia' else [6, 8]
    rem = F(94); t = F(0); i = 0
    while True:
        r = rates[i % 2]
        if rem <= r:
            return t + rem / r
        rem -= r; t += 1; i += 1
show('G1-25', 'jia first', sim25('jia'), 'yi first', sim25('yi'))
