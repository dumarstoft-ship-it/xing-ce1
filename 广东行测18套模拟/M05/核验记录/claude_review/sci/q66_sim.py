# Q66 blind check: box on floor, horizontal pull F(t) shaped like the figure
# (0 -> rises -> crosses f at t1 -> peak 2f at t2 -> falls, crosses f at t3 -> tends to 0).
# f_static_max == f_kinetic == f. Simulate friction and acceleration.
import math
m, f = 1.0, 1.0
t2 = 2.0
def F(t):
    # peak 2f at t2, zero slope at 0, long tail
    x = t / t2
    return 2 * f * x**2 * math.exp(1 - x**2) if x <= 1 else 2 * f / (1 + 1.2 * (x - 1)**1.5 * 2)
dt = 1e-4
t, v = 0.0, 0.0
rows = []
amax, tamax = -1e9, None
fr_log = []
t1 = t3 = None
prevF = 0
while t < 12:
    Ft = F(t)
    if v <= 1e-12 and Ft <= f + 1e-12:
        fric = Ft; a = 0.0; state = 'static'; v = 0.0
    else:
        fric = f; a = (Ft - f) / m; state = 'sliding'
    if t1 is None and Ft >= f: t1 = t
    if t1 is not None and t3 is None and t > t2 and Ft <= f: t3 = t
    if abs(a) > amax: amax, tamax = abs(a), t
    fr_log.append((t, Ft, fric, a, v, state))
    v += a * dt
    if v < 0: v = 0.0
    t += dt
print(f"t1~{t1:.3f}, t2={t2}, t3~{t3:.3f}")
print(f"max |a| = {amax:.4f} at t = {tamax:.3f}  (expected f/m = {f/m} at t2)")
for tt in [0.5, 1.0, t1 - 0.01, t1 + 0.01, 1.8, t2, 2.5, t3 - 0.01, t3 + 0.01, 5, 8, 11.9]:
    i = int(round(tt / dt))
    r = fr_log[i]
    print(f"t={r[0]:6.3f} F={r[1]:.3f} friction={r[2]:.3f} a={r[3]:+.3f} v={r[4]:.3f} {r[5]}")
fr_in = [r[2] for r in fr_log if t1 < r[0] < t3]
print("friction in (t1,t3): min=%.4f max=%.4f  -> constant = sliding friction f" % (min(fr_in), max(fr_in)))
stop = next((r[0] for r in fr_log if r[0] > t3 and r[5] == 'static'), None)
print("box stops again at t ~", stop)
