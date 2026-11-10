from fractions import Fraction as F
from scipy.optimize import linprog

print("=== G3-01 alt: each machine makes complete sets only ===")
r1 = 1 / (F(1, 8) + F(1, 4)); r2 = 1 / (F(1, 4) + F(1, 6))
print("sets/h", r1, r2, "time", F(40) / (r1 + r2), float(F(40) / (r1 + r2)))
# discrete check on a fine grid: finished parts are integers at time T, T on 1-minute grid
def feasible(Tmin):
    # 甲 spends a minutes on A, rest on B; 乙 spends b minutes on A, rest on B
    for a in range(0, Tmin + 1):
        A1 = (8 * a) // 60; B1 = (4 * (Tmin - a)) // 60
        need_A = max(0, 40 - A1)
        # 乙 minutes on A needed
        b = -(-need_A * 60 // 4)
        if b > Tmin: continue
        B2 = (6 * (Tmin - b)) // 60
        if B1 + B2 >= 40:
            return True
    return False
for Tm in range(300, 480):
    if feasible(Tm):
        print("discrete minute-grid min T =", Tm, "min =", F(Tm, 60), "h")
        break

print("=== G3-08 alt: no batch rule, only integer items & exact 10% ===")
best = 0
for N in range(0, 400):
    if N % 10: continue
    t = N * F(3, 2) + (N // 10) * F(3, 4)
    if t <= 420: best = N
print("max N with exact 10% rework:", best)

print("=== G3-35 general LP over time grid (step 0.1 day) ===")
# discretize time into slots of 0.1 day up to 20 days; variables per slot:
# jf[s] (甲 front fraction), jb[s] (甲 back), y[s] (乙 front), z[s] (丙 back)
# 甲 leave rule handled by enumerating leave slot L: jf allowed only s<L, jb only s>=L+20
# front must finish by slot Fs before any back work: enumerate Fs
import itertools
step = F(1, 10)
best = None
for Fs in range(50, 90):       # front completion slot
    for L in range(0, Fs + 1): # 甲 leaves front at slot L (<= Fs)
        front = 3 * step * L + 2 * step * Fs
        if front < 30: continue
        arrive = L + 20
        # back starts at Fs; 丙 from Fs, 甲 from max(arrive, Fs)
        s = max(arrive, Fs)
        w = (s - Fs) * step
        E = s * step + (30 - w) / 4 if w < 30 else Fs * step + 30
        if best is None or E < best[0]:
            best = (E, L * step, Fs * step)
print("grid best E", best, float(best[0]))
