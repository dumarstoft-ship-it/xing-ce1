"""Q44: circular track 400 m, a tree every 8 m on the outside; a 24 m stretch cannot be planted.
Maximum number of trees. Two models x two boundary conventions:
  model 1 (periodic): trees at t + 8k all round the loop, drop those inside the stretch;
  model 2 (chain): the plantable arc (400-24 = 376 m) unrolled into a segment, trees 8 m apart on it.
  ends_ok=True : the two end points of the 24 m stretch may carry a tree (stretch = open interval)
  ends_ok=False: they may not (stretch = closed interval).
Positions in units of 0.5 m so everything stays integer."""
U = 2
L, gap, step = 400 * U, 24 * U, 8 * U

def in_stretch(x, ends_ok):
    x %= L
    return (0 < x < gap) if ends_ok else (0 <= x <= gap)

res = {}
for ends_ok in (True, False):
    best1 = max(sum(not in_stretch(t + k * step, ends_ok) for k in range(L // step)) for t in range(step))
    seg = L - gap                       # 376 m in 0.5 m units
    best2 = 0
    for u0 in range(0, seg + 1):        # first tree at distance u0 from one end of the segment
        if not ends_ok and u0 == 0:
            continue
        lim = seg if ends_ok else seg - 1
        n = (lim - u0) // step + 1 if u0 <= lim else 0
        best2 = max(best2, n)
    res[ends_ok] = (best1, best2)
    print(f"ends of stretch plantable={ends_ok}: periodic model max={best1}, chain model max={best2}")

assert res[True] == (48, 48) and res[False] == (47, 47)
print("standard reading: 400-24 = 376 m segment, both ends planted: 376/8 + 1 =", 376 // 8 + 1)
print("equivalently: 50 trees on the full loop, the 24 m = 3 gaps stretch only removes the 2 interior trees -> 48")
opts = {"A": 46, "B": 47, "C": 48, "D": 49}
print("ANSWER: C (48); 47 only if the two ends of the 24 m stretch were also forbidden")
