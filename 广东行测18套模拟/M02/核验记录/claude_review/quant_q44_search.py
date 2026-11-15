"""Q44: 9 months, total 234, max = k*min (k=3 for '多2倍'), rank7+rank8 = max, all pairwise gaps >= 2.
Pruned integer DFS + real-valued LP."""
import sys

def dfs_all(m, k=3, total=234, gap=2, pair=(6, 7), limit=5):
    """descending a[0]=k*m > a[1] > ... > a[8]=m, gaps>=gap, a[pair0]+a[pair1]==a[0], sum==total.
    Returns up to `limit` solutions (integers)."""
    a1 = k*m
    sols = []
    def rec(seq, s):
        n = len(seq)
        if n == 8:
            if seq[-1] - m < gap: return
            full = seq + [m]
            if s + m == total and full[pair[0]] + full[pair[1]] == a1:
                sols.append(full)
            return
        r = 8 - n  # remaining free slots before a9 (positions n..7)
        hi = seq[-1] - gap
        lo = m + gap*r
        if hi < lo: return
        for v in range(hi, lo-1, -1):
            # bounds on remaining sum after choosing v: positions n+1..7 count r-1
            rr = r - 1
            maxrest = sum(v - gap*(i+1) for i in range(rr))
            minrest = sum(m + gap*(i+1) for i in range(rr))
            need = total - m - s - v
            if need > maxrest: break        # v descending: further v smaller -> maxrest smaller
            if need < minrest: continue
            rec(seq + [v], s + v)
            if len(sols) >= limit: return
    rec([a1], a1)
    return sols

for k in (3, 2):
    found = False
    for m in range(1, 60):
        s = dfs_all(m, k=k)
        if s:
            print(f"k={k} desc-rank(7,8): min integer m = {m}; examples {s[:3]}")
            found = True
            break
    if not found:
        print(f"k={k} desc-rank(7,8): no integer solution for m<60")

# ascending reading: 7th & 8th smallest = 3rd & 2nd largest -> indices 2,1 in descending
for k in (3,):
    for m in range(1, 80):
        s = dfs_all(m, k=k, pair=(1, 2))
        if s:
            print(f"k={k} asc-rank: min integer m = {m}; examples {s[:2]}")
            break
    else:
        print("asc-rank: none")

# count all integer solutions at m=12 (k=3)
alls = dfs_all(12, k=3, limit=10**6)
print("m=12 integer solutions:", len(alls))
for x in alls: print("  ", x)

# real-valued LP
try:
    from scipy.optimize import linprog
    import numpy as np
    for k in (3, 2):
        c = np.zeros(9); c[8] = 1
        A_ub, b_ub = [], []
        for i in range(8):
            row = np.zeros(9); row[i+1] = 1; row[i] = -1
            A_ub.append(row); b_ub.append(-2)
        A_eq, b_eq = [], []
        row = np.zeros(9); row[0] = 1; row[8] = -k; A_eq.append(row); b_eq.append(0)
        row = np.zeros(9); row[6] = 1; row[7] = 1; row[0] = -1; A_eq.append(row); b_eq.append(0)
        A_eq.append(np.ones(9)); b_eq.append(234)
        r = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=[(0, None)]*9)
        print(f"LP k={k}: status={r.status} {r.message}", None if r.x is None else (round(r.fun, 6), [round(v, 3) for v in r.x]))
except Exception as e:
    print("scipy not available:", e)
