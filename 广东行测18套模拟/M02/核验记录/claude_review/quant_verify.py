from fractions import Fraction as F
from itertools import combinations, permutations, product
import math

print("== Q31 ==")
s = [9, 7, 11, 3, None, -13]
for opt, x in zip("ABCD", [4, 19, 25, -6]):
    t = s[:]; t[4] = x
    d = [t[i+1]-t[i] for i in range(5)]
    r = [F(d[i+1], d[i]) for i in range(4) if d[i] != 0]
    rec = all(t[i+2] == 2*t[i]-t[i+1] for i in range(4))
    print(opt, x, "diffs", d, "ratios", [str(v) for v in r], "rec2a-b", rec)

print("== Q32 ==")
for opt, x in zip("ABCD", [102, 103, 104, 105]):
    t = [12, 18, 29, 46, 70, x]
    d1 = [t[i+1]-t[i] for i in range(5)]
    d2 = [d1[i+1]-d1[i] for i in range(4)]
    print(opt, x, d1, d2)

print("== Q33 ==")
t = [9, 63, 217, 511]
print([(n, (2*(i+1))**3 + (-1)**i) for i, n in enumerate(t)], "next", 10**3 + 1)

print("== Q34 ==")
seq = [F(4), F(2), F(8, 5), F(10, 7), F(4, 3)]
print([F(2*(n+1), 2*n-1) for n in range(1, 7)], [str(x) for x in seq])

print("== Q35 ==")
t = [3]
for k in range(2, 7):
    t.append(t[-1]*k + (k-1))
print(t, [4*math.factorial(n)-1 for n in range(1, 7)])

print("== Q36 ==")
A = (400, F(40)); B = (200, F(60))
def pour(src, dst, x, cap=500):
    vs, als = src; vd, ald = dst
    if x > vs or vd + x > cap:
        return None
    c = als/vs
    return (vd+x, ald + c*x)
for name, (s_, d_, x) in {"A:B->A300": (B, A, 300), "B:A->B300": (A, B, 300), "C:B->A100": (B, A, 100), "D:A->B100": (A, B, 100)}.items():
    r = pour(s_, d_, x)
    print(name, None if r is None else (r[0], float(r[1]/r[0])))

print("== Q37 ==")
for N in range(1, 100):
    if N % 13: continue
    if (15*N) % 26: continue
    ch = 15*N//26
    if ch % 9: continue
    m_ch = ch*4//9; f_ch = ch*5//9
    males = 7*N//13
    print("N", N, "changers", ch, "m", m_ch, "f", f_ch, "males", males, "nonchange males", males-m_ch)

print("== Q38 ==")
# event simulation with exact rationals: positions on [0,D], 甲 from 0, 乙 from D.
def meetings(D, v1, v2, tmax, include_catchup=True):
    # piecewise linear; step by small rational events: compute all times when positions equal.
    # positions are triangle waves; meeting times solved per interval between turn events.
    def pos(v, start, t):
        # start 0 or D, moving inward
        period = 2*D/v
        tt = (t % period) if not isinstance(t, F) else t - period*math.floor(t/period)
        d = v*tt
        if d <= D:
            p = d
        else:
            p = 2*D - d
        return p if start == 0 else D - p
    # turn times
    ev = set([F(0)])
    k = 1
    while True:
        t1 = k*D/v1
        if t1 > tmax: break
        ev.add(F(t1)); k += 1
    k = 1
    while True:
        t2 = k*D/v2
        if t2 > tmax: break
        ev.add(F(t2)); k += 1
    ev = sorted(ev) + [F(tmax)]
    res = []
    for a, b in zip(ev, ev[1:]):
        if a == b: continue
        mid = (a+b)/2
        # velocities on interval
        pa1, pb1 = pos(v1, 0, a), pos(v1, 0, b)
        pa2, pb2 = pos(v2, 'D', a), pos(v2, 'D', b)
        s1 = (pb1-pa1)/(b-a); s2 = (pb2-pa2)/(b-a)
        if s1 == s2:
            continue
        t = a + (pa2-pa1)/(s1-s2)
        if a < t <= b:
            kind = "face" if s1*s2 < 0 else "catch"
            res.append((t, pos(v1, 0, t), kind))
    return res
for D in [2400, 2640, 2880, 3300]:
    v = F(D, 30)  # combined speed per minute
    v1 = v*F(6, 11); v2 = v*F(5, 11)
    ms = meetings(F(D), v1, v2, F(200))
    first, second = ms[0], ms[1]
    print(D, "first", first[0], float(first[1]), first[2], "| second", second[0], float(second[1]), second[2], "| gap", float(abs(first[1]-second[1])),
          "| jia to B after first:", float((D-first[1])/v1))

print("== Q39 ==")
c1 = F(260)/F(13, 10); prof = 260 - c1
c2 = prof/F(1, 4); p2 = c2*F(3, 4)
print(c1, prof, c2, p2, 260+p2)

print("== Q40 ==")
for L in [120, 100, 90, 80]:
    w = t_ = l = 0
    for x in range(0, L+1):
        a, b = x % 3 == 0, x % 5 == 0
        if a and b: l += 1
        elif a: w += 1
        elif b: t_ += 1
    print(L, "end laser" if L % 15 == 0 else "end not laser", w, t_, l, 80*w+150*t_+700*l)

print("== Q41 ==")
yi = F(1); jia = 2*yi; bing = (4*jia + 2*yi)/3
W = 4*jia + 2*yi + 4*bing
print("bing", bing, "W", W)
for x in range(0, 11):
    # 乙 works all 10 days (max), 丙 x days
    print(x, float(10*yi + x*bing), "ok" if 10*yi + x*bing >= W else "")
print("simultaneous days", float(W/(yi+bing)))

print("== Q42 ==")
people = ["M1", "M2", "M3", "F1", "F2", "F3", "F4", "F5"]
cnt = 0
for host in [p for p in people if p[0] == "F"]:
    rest = [p for p in people if p != host]
    for aw in combinations(rest, 4):
        g = sum(1 for p in aw if p[0] == "F")
        if g >= 4-g:
            cnt += 1
print(cnt)

print("== Q43 ==")
# exact enumeration of state vectors
from collections import Counter
cups = 5
pairs = list(combinations(range(cups), 2))
dist = Counter({(0,)*cups: F(1)})
for step in range(3):
    nd = Counter()
    for st, pr in dist.items():
        for pa in pairs:
            s2 = list(st)
            for i in pa: s2[i] ^= 1
            nd[tuple(s2)] += pr/len(pairs)
    dist = nd
p_down0 = sum(pr for st, pr in dist.items() if st[0] == 0)
print("P(designated cup down)", p_down0)
print("P(all down)", dist[(0,)*5], "P(all up)", dist.get((1,)*5, 0))
# other possible original questions
from collections import defaultdict
byups = defaultdict(F)
for st, pr in dist.items(): byups[sum(st)] += pr
print("distribution of #up:", {k: str(v) for k, v in sorted(byups.items())})
print("expected #down", sum((5-k)*v for k, v in byups.items()))

print("== Q45 ==")
import cmath
A_ = complex(0, math.sqrt(3)); D_ = complex(-1, 0); E_ = complex(1, 0)
B_ = (A_ + D_)/2; C_ = (A_ + E_)/2
# intersection of BE and CD
def inter(p1, p2, p3, p4):
    x1, y1, x2, y2, x3, y3, x4, y4 = p1.real, p1.imag, p2.real, p2.imag, p3.real, p3.imag, p4.real, p4.imag
    den = (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
    px = ((x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4))/den
    py = ((x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4))/den
    return complex(px, py)
O_ = inter(B_, E_, C_, D_)
def area(pts):
    s = 0
    for i in range(len(pts)):
        a, b = pts[i], pts[(i+1) % len(pts)]
        s += a.real*b.imag - b.real*a.imag
    return abs(s)/2
ya = area([A_, B_, O_, C_]); tot = area([A_, D_, E_])
print("yellow/blue", ya/(tot-ya))
