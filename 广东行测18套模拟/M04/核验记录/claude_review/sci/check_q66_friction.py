"""Q66: F on lower block A grows from 0; B rides on A; ground friction coefficient uniform.
Prints friction on A (from ground) and on B (from A) in static and accelerating phases,
for (i) F keeps increasing, (ii) F stops increasing once motion starts (to test the clarify edit).
Run: python3 check_q66_friction.py
"""
g = 9.8
mA, mB = 2.0, 1.0
mu_s, mu_k = 0.35, 0.30      # ground: max static >= kinetic (uniform roughness)
mu_AB_s = 0.5                # A-B max static coefficient (finite -> B would eventually slip)
N = (mA + mB) * g
f_ground_max = mu_s * N

def state(F, moving):
    if not moving and F <= f_ground_max:
        return dict(phase='static', f_ground_on_A=F, f_on_B=0.0, a=0.0)
    a = (F - mu_k * N) / (mA + mB)
    return dict(phase='accel', f_ground_on_A=mu_k * N, f_on_B=mB * a, a=a)

print('ground max static %.2f N, kinetic %.2f N, B slips on A when f_on_B > %.2f N' % (f_ground_max, mu_k * N, mu_AB_s * mB * g))
for label, F_of_t in [('(i) F keeps increasing', lambda t: 2.0 * t),
                      ('(ii) F stops at onset value', None)]:
    print('---', label)
    moving = False; F_stop = None
    for t in range(0, 11):
        if F_of_t:
            F = F_of_t(t)
        else:
            F = 2.0 * t if F_stop is None else F_stop
        s = state(F, moving)
        if s['phase'] == 'accel' and not moving:
            moving = True
            if F_of_t is None:
                F_stop = F
        slip = s['f_on_B'] > mu_AB_s * mB * g
        print('t=%2d F=%5.2f phase=%-6s f_ground->A=%5.2f f_A->B=%5.2f a=%5.2f %s' % (
            t, F, s['phase'], s['f_ground_on_A'], s['f_on_B'], s['a'], 'B WOULD SLIP' if slip else ''))
