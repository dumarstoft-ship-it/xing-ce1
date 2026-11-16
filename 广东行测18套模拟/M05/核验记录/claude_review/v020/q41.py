from itertools import combinations, permutations
ages = [24, 26, 29, 32, 34, 36]

def count(avg_strict=True, diff_inclusive=True, use_avg=True, use_diff=True):
    sets = []
    for c in combinations(ages, 3):
        s = sum(c)
        rng = max(c) - min(c)
        ok_avg = (s > 84) if avg_strict else (s >= 84)
        ok_diff = (rng <= 10) if diff_inclusive else (rng < 10)
        if (ok_avg or not use_avg) and (ok_diff or not use_diff):
            sets.append(c)
    # ordered: permutations of each set
    perms = sum(1 for c in sets for _ in permutations(c))
    return sets, perms

print("All 20 combos:")
for c in combinations(ages, 3):
    print(c, "sum", sum(c), "avg %.2f" % (sum(c)/3), "range", max(c)-min(c))

for label, kw in [
    ("Correct: avg>28, diff<=10", dict()),
    ("diff<10 (misread 不超过)", dict(diff_inclusive=False)),
    ("avg>=28 (misread 超过)", dict(avg_strict=False)),
    ("both misread", dict(avg_strict=False, diff_inclusive=False)),
    ("ignore avg", dict(use_avg=False)),
    ("ignore diff", dict(use_diff=False)),
]:
    sets, perms = count(**kw)
    print(f"{label}: {len(sets)} sets -> {perms} ordered; x36 (order AND topic) = {len(sets)*36}")
