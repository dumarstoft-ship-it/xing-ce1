from fractions import Fraction as F
import itertools, datetime

def show(bid, *a):
    print(bid, *a)

# G1-26: piecewise simulation in 1/60 h steps exact via fractions
def working(t, on, off):
    # t: Fraction hours, machine works [k(on+off), k(on+off)+on)
    per = on + off
    return (t % per) < on

def cum26(T):
    # integrate exactly over unit-minute grid (rates constant within minutes since boundaries are integers of hours)
    total = F(0)
    t = F(0)
    step = F(1, 60)
    while t < T:
        dt = min(step, T - t)
        if working(t, 3, 1):
            total += 9 * dt
        if working(t, 4, 2):
            total += 6 * dt
        t += dt
    return total

# find exact finish time: scan hours then solve within
t = F(0)
cum = F(0)
while True:
    r = (9 if working(t, 3, 1) else 0) + (6 if working(t, 4, 2) else 0)
    # next breakpoint: next integer hour
    nxt = t + 1
    if cum + r * (nxt - t) >= 153:
        fin = t + (153 - cum) / r
        break
    cum += r * (nxt - t)
    t = nxt
show('G1-26', 'finish hours', fin, '=', int(fin), 'h', (fin - int(fin)) * 60, 'min', 'check', cum26(fin))

# G1-27 flow shop simulation
pA, pB, pC = 3, 5, 4
fa = fb = fc = 0
for i in range(30):
    fa = fa + pA
    fb = max(fa, fb) + pB
    fc = max(fb, fc) + pC
show('G1-27', 'makespan', fc)

# G1-28
pack_done = [2 * (k + 1) for k in range(20)]
truck_free = 0
arrivals = []
for batch in range(4):
    ready = pack_done[batch * 5 + 4]
    dep = max(ready, truck_free)
    arr = dep + 6
    truck_free = arr + 4
    arrivals.append((dep, arr))
show('G1-28', arrivals)

# G1-29: 2024-07-05 is Friday
d = datetime.date(2024, 7, 5)
assert d.weekday() == 4
idx = 0  # xiaoling at idx 0
k = 0
cur = d
while True:
    cur += datetime.timedelta(days=1)
    if cur.weekday() >= 5:
        continue
    k += 1
    if k % 4 == 0 and cur.weekday() == 0:
        show('G1-29', cur)
        break
# also for any year where Jul 5 is a Friday: month/day result is the same since no month boundary

# G1-30
plan = [2, 3, 3, 1, 1]
tot = sum(plan[(d - 1) % 5] for d in range(1, 85) if d % 7 != 0)
show('G1-30', tot, 'plan total', sum(plan[(d - 1) % 5] for d in range(1, 85)))

# G1-31: LP over switch patterns with scipy
from scipy.optimize import linprog
best = None
# patterns for each worker: 'A','B','AB' (both, with 1h setup); more switches never help
for pj in ['A', 'B', 'AB']:
    for py in ['A', 'B', 'AB']:
        # vars: T, a1, b1, a2, b2 ; minimize T
        c = [1, 0, 0, 0, 0]
        A_ub = []; b_ub = []
        # time constraints
        s1 = 1 if pj == 'AB' else 0
        s2 = 1 if py == 'AB' else 0
        A_ub.append([-1, 1, 1, 0, 0]); b_ub.append(-s1)
        A_ub.append([-1, 0, 0, 1, 1]); b_ub.append(-s2)
        # production
        A_ub.append([0, -12, 0, -6, 0]); b_ub.append(-84)
        A_ub.append([0, 0, -8, 0, -6]); b_ub.append(-76)
        bounds = [(0, None)]
        bounds.append((0, None) if 'A' in pj else (0, 0))
        bounds.append((0, None) if 'B' in pj else (0, 0))
        bounds.append((0, None) if 'A' in py else (0, 0))
        bounds.append((0, None) if 'B' in py else (0, 0))
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
        if res.status == 0:
            print('  G1-31 pattern', pj, py, round(res.fun, 6), [round(v, 4) for v in res.x])
            if best is None or res.fun < best[0] - 1e-9:
                best = (res.fun, pj, py)
show('G1-31', 'best', best)
# also brute force with up to 2 switches each in a discretized way (segments of 0.5h) to confirm nothing beats 10
def brute31(step=F(1, 4), Tmax=F(10)):
    # check whether T < 10 feasible: with any number of switches, each switch wastes 1h; total A-time and B-time per worker matter only
    # worker with both products loses >=1h. So enumerate (uses both?) and continuous split -> same as LP. done.
    pass

# G1-32
tasks = [3, 4, 6, 8, 11]
best = None
allres = {}
for mask in range(1, 31):
    S = [tasks[i] for i in range(5) if mask >> i & 1]
    R = [tasks[i] for i in range(5) if not mask >> i & 1]
    tj = sum(S) + (len(S) - 1) * 1
    ty = sum(R) + (len(R) - 1) * 2
    m = max(tj, ty)
    allres.setdefault(m, []).append((S, R, tj, ty))
mn = min(allres)
show('G1-32', 'min', mn, allres[mn])
for opt in [17, 18, 19, 20]:
    print('   achievable', opt, opt in allres, 'min<=opt', mn <= opt)

# G1-33
best = None
for x in range(0, 9):
    for y in range(0, 9 - x):
        if 5 * (8 * x + 12 * y) >= 410:
            cost = 5 * (100 * x + 160 * y)
            if best is None or cost < best[0]:
                best = (cost, [(x, y)])
            elif cost == best[0]:
                best[1].append((x, y))
show('G1-33', best)

# G1-34
res = []
for k in range(0, 7):
    res.append((k, max(F(36, 8 - k), F(60, 10 + k))))
show('G1-34', [(k, str(v), float(v)) for k, v in res])
# alt: finished group may help
res2 = []
for k in range(0, 7):
    t1, t2 = F(36, 8 - k), F(60, 10 + k)
    if t1 <= t2:
        T = t1 + (60 - (10 + k) * t1) / 18
    else:
        T = t2 + (36 - (8 - k) * t2) / 18
    res2.append((k, str(T)))
show('G1-34 alt (finished group helps)', res2)
