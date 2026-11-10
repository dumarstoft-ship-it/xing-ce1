from fractions import Fraction as F

# G1-35: time t in minutes from jia's start; yi starts at t=-15
def f_jia(t):
    t = F(t)
    if t <= 0:
        return F(0)
    pos = F(0)
    segs = [(0, 30), (45, 75), (90, 120)]
    for a, b in segs:
        if t >= b:
            pos += F(b - a, 10)
        elif t > a:
            pos += (t - a) / 10
    return min(pos, F(9))

def g_yi(t, T):
    v = F(9) / T
    t = F(t)
    if t <= -15:
        return F(0)
    return min(F(9), v * (t + 15))

def meetings(T):
    T = F(T)
    tB = T - 15
    bps = sorted(set([F(-15), F(0), F(30), F(45), F(75), F(90), F(120), tB, F(max(200, tB + 10))]))
    bps = [b for b in bps if b >= -15]
    zeros = []
    intervals = []
    for a, b in zip(bps, bps[1:]):
        Da = g_yi(a, T) - f_jia(a)
        Db = g_yi(b, T) - f_jia(b)
        mid = (a + b) / 2
        Dm = g_yi(mid, T) - f_jia(mid)
        if Da == 0 and Db == 0 and Dm == 0:
            intervals.append((a, b))
            continue
        if Da == 0:
            zeros.append(a)
        if Db == 0:
            zeros.append(b)
        if (Da < 0 < Db) or (Db < 0 < Da):
            tz = a + (b - a) * (-Da) / (Db - Da)
            zeros.append(tz)
    # filter: exclude positions 0 (start) and 9 (end)
    pts = set()
    for z in zeros:
        p = f_jia(z)
        if 0 < p < 9:
            pts.add(z)
    ints = [(a, b) for a, b in intervals if 0 < f_jia((a + b) / 2) < 9]
    return sorted(pts), ints

for T in [75, 120, 135, 150, 180]:
    pts, ints = meetings(T)
    print('G1-35 option T=', T, 'meetings', len(pts), [(str(z), str(f_jia(z))) for z in pts], ints)

# scan T on a fine grid
exact2 = []
prev = None
segments = []
Ts = [F(k, 8) for k in range(8 * 60, 8 * 400 + 1)]
specials = [F(9) / v for v in [F(1, 15), F(1, 20), F(2, 35)]]
Ts = sorted(set(Ts + specials))
for T in Ts:
    n = len(meetings(T)[0])
    if n == 2:
        exact2.append(T)
    if n != prev:
        segments.append((T, n))
        prev = n
print('G1-35 count changes (T start, count):', [(str(a), n) for a, n in segments])
print('G1-35 T with exactly 2 meetings:', [str(t) for t in exact2])
