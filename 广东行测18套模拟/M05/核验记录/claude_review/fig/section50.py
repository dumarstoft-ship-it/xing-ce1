# Q50: reconstructed solid (units: X width, d depth, h height; cabinet drawing: 1 unit = 20px front, 7px+7px receding)
# pixel evidence (orig px): lower block front x24..86,y82..102 (d=0); ramp edges (25,82)->(39,48) & (65,82)->(79,48);
# flat-top left edge (79,68)->(65,82); back block top front edge y=48 x39..99 (d=2); tall block front x91..113 y54..95 (d=1);
# small box front x39..61 y28..48 (d=2), top back edge y=21 (d=3); P=(67,21), Q=(25,102), R=(85,102)
import numpy as np
def inside(X, d, h):
    if h < 0: return False
    # lower part X0..3, d0..2 : ramp on X0..2 top = 1 + d/2 ; flat top 1 on X2..3
    if 0 <= X <= 2 and 0 <= d <= 2 and h <= 1 + d / 2: return True
    if 2 <= X <= 3 and 0 <= d <= 2 and h <= 1: return True
    if 0 <= X <= 3 and 2 <= d <= 3 and h <= 2: return True       # back block
    if 3 <= X <= 4 and 1 <= d <= 3 and h <= 2: return True       # tall block (set back by 1)
    if 0 <= X <= 1 and 2 <= d <= 3 and 2 <= h <= 3: return True  # small cube on back block
    return False
P = np.array([1, 3, 3.]); Q = np.array([0, 0, 0.]); R = np.array([3, 0, 0.])
n = np.cross(R - Q, P - Q); print('plane normal (X,d,h):', n, ' => h = d' if abs(n[1] + n[2]) < 1e-9 else '')
# sample the plane h = d ; section coordinates (X, s=d)
N = 60
rows = []
for k in range(int(3.2 * N), -1, -1):
    d = k / N
    row = ''
    for j in range(int(4.2 * N) + 1):
        X = j / N
        # strict interior test with tiny epsilon to drop zero-area contacts
        eps = 1e-6
        row += '#' if inside(X, d, d - eps) and inside(X, d + eps, d - 2*eps) else '.'
    rows.append((d, row))
for d, row in rows[::6]:
    print('s=%.2f ' % d + row[::3])
# column extents
for X in (0.5, 1.5, 2.5, 3.5):
    ds = [k / 600 for k in range(0, 1900) if inside(X, k / 600, k / 600 - 1e-6) and inside(X, k / 600 + 1e-6, k / 600 - 2e-6)]
    print('X=%.1f: section d from %.3f to %.3f' % (X, min(ds), max(ds)))
# sensitivity: measured-pixel model (back block top drawn at h=41/20, plane through P at h=60/20,d=21/7)
print('measured-pixel check: plane height at d=2 is %.3f units vs back-block top 41/20=%.3f' % (60/20*2/3, 41/20))
# area-bearing intervals: sample d at offsets avoiding lattice values; merge runs
print('area-bearing section intervals (sampling d at k/600+1/1200):')
for X in (0.5, 1.5, 2.5, 3.5):
    ds = [k / 600 + 1/1200 for k in range(0, 1900)]
    ins = [inside(X, d, d) for d in ds]
    runs = []; start = None
    for d, v in zip(ds, ins):
        if v and start is None: start = d
        if not v and start is not None: runs.append((round(start, 2), round(prev, 2))); start = None
        prev = d
    if start is not None: runs.append((round(start, 2), round(prev, 2)))
    print('  X=%.1f: %s' % (X, runs))
print('pieces touch only at (X=3, s=1): column X2..3 top s=1 meets tall-block piece bottom s=1 at a single corner point')
