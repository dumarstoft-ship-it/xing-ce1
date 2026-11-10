from fractions import Fraction as F
from itertools import permutations, product, combinations
from scipy.optimize import linprog
import math

print("=== G2-25 ===")
rates = [F(1, 12), F(1, 18), F(1, 36)]
done = F(0); t = F(0); k = 0
while True:
    r = rates[k % 3]
    if done + r >= 1:
        t += (1 - done) / r
        break
    done += r; t += 1; k += 1
print("total hours", t)

print("=== G2-26 ===")
J = [2, 4, 5, 7]; Y = [6, 3, 4, 9]
res = []
for mask in product([0, 1], repeat=4):
    if all(m == 0 for m in mask) or all(m == 1 for m in mask):
        continue
    tj = sum(J[i] for i in range(4) if mask[i] == 0)
    ty = sum(Y[i] for i in range(4) if mask[i] == 1)
    res.append((max(tj, ty), mask))
res.sort()
print(res[:4])

print("=== G2-27 ===")
a = [2, 4, 3]; b = [6, 2, 5]
def makespan(o1, o2):
    # non-permutation allowed: o1 order on machine1, o2 order on machine2
    f1 = {}
    t = 0
    for i in o1:
        t += a[i]; f1[i] = t
    t2 = 0
    for i in o2:
        t2 = max(t2, f1[i]) + b[i]
    return t2
res = sorted((makespan(p, q), p, q) for p in permutations(range(3)) for q in permutations(range(3)))
print(res[:3])

print("=== G2-28 ===")
# sizes distinct >=3 summing 150 over 15 units -> forced 3..17
print(sum(range(3, 18)))
sizes = list(range(3, 18))
# min number of units containing 50 A grads: choose k largest units capacity >= 50
for k in range(1, 16):
    if sum(sorted(sizes, reverse=True)[:k]) >= 50:
        print("min units for A:", k)
        break
# feasibility: A: 17,16,15 full + 2 in 14 ; B, C share remaining 100 capacity, 50 each -> greedy check
rem = {s: s for s in sizes}
for s in [17, 16, 15]:
    rem[s] = 0
rem[14] -= 2
print("remaining capacity", sum(rem.values()))

print("=== G2-29 ===")
def ok(row):
    n = len(row)
    for i, v in enumerate(row):
        if v == 0:
            occ = 0
            if i > 0 and row[i - 1] == 1: occ += 1
            if i < n - 1 and row[i + 1] == 1: occ += 1
            if occ != 1:
                return False
    return True
# DP over length n with exactly 9 occupied: brute force via DP states (prev2, prev1, count)
def feasible(n, k=9):
    # build all rows via DP with state (last two cells, count, pending-check)
    # simpler: recursive generation with pruning
    from functools import lru_cache
    @lru_cache(None)
    def go(i, p2, p1, cnt):
        # cells 0..i-1 placed; p2 = cell i-2, p1 = cell i-1 (None if not exist)
        if cnt > k:
            return False
        if i == n:
            # check last cell (i-1) if empty: its neighbors are i-2 only
            if p1 == 0:
                occ = (1 if p2 == 1 else 0)
                if occ != 1: return False
            return cnt == k
        for v in (0, 1):
            # when placing cell i, we can check cell i-1
            if p1 == 0:
                occ = (1 if p2 == 1 else 0) + (1 if v == 1 else 0)
                if occ != 1:
                    continue
            if go(i + 1, p1, v, cnt + v):
                return True
        return False
    return go(0, None, None, 0)
mx = max(n for n in range(9, 60) if feasible(n))
print("max n", mx, [n for n in range(9, 40) if feasible(n)])
# double-check with an explicit row
row = [0] + sum(([1, 0, 0] for _ in range(8)), []) + [1, 0]
print(len(row), sum(row), ok(row))

print("=== G2-30 ===")
res = []
for x in range(0, 10):
    for y in range(0, 10):
        prod = F(5, 10) * x + F(7, 10) * y
        waste = F(4, 10) * x + F(3, 10) * y
        if prod >= F(19, 10) and waste <= 1:
            res.append((F(3, 10) * x + F(4, 10) * y, x, y))
res.sort()
print([(float(c), x, y) for c, x, y in res[:4]])

print("=== G2-31 ===")
def flow(times, n=24):
    m = len(times)
    C = [[0] * m for _ in range(n)]
    for i in range(n):
        for k in range(m):
            prev_job = C[i - 1][k] if i > 0 else 0
            prev_stage = C[i][k - 1] if k > 0 else 0
            C[i][k] = max(prev_job, prev_stage) + times[k]
    return C[-1][-1]
base = [4, 7, 5]
for k in range(3):
    t = base[:]; t[k] -= 2
    print("reduce machine", k + 1, t, flow(t))
print("no reduction", flow(base))

print("=== G2-32 ===")
# LP: days 1..10; xJ_d, xY_d person-days, extra e from day 7..10
# minimal integer e: total capacity 200 + 4e >= 244 and Jia only in days 1..6
for e in range(0, 15):
    capJ = 20 * 6
    if capJ < 84:
        continue
    yi_cap = (capJ - 84) + (20 + e) * 4
    if yi_cap >= 160:
        print("min extra", e, "yi capacity", yi_cap)
        break

print("=== G2-33 ===")
for total in [17, 18, 19, 24]:
    w = total - 1
    print(total, "ratio new/old", F(w, w + 6))

print("=== G2-34 ===")
r = linprog([180, 165], A_ub=[[-18, -15]], b_ub=[-144], bounds=[(0, 6), (0, 6)])
print(r.x, r.fun)

print("=== G2-35 ===")
Yt = [2, 3, 5, 7, 9, 10]
best = None
for mask in product([0, 1], repeat=6):
    if sum(mask) in (0, 6):
        continue
    tj = F(sum(Yt[i] for i in range(6) if mask[i] == 1), 2)
    ty = sum(Yt[i] for i in range(6) if mask[i] == 0)
    v = max(tj, ty)
    if best is None or v < best[0]:
        best = (v, mask)
print(best)
