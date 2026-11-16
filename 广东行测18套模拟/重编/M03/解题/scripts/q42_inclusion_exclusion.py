"""Q42: S = households that sort garbage, D = households that use degradable bags.
|S| = |D| + 18; |D only| = 30; |S and D| = 60% of |D|; neither = 20. Total households?
options A80 B108 C123 D143
Enumerate the four Venn regions directly."""
sols = []
for both in range(0, 300):
    for s_only in range(0, 300):
        d_only = 30
        D = d_only + both
        S = s_only + both
        if S != D + 18:
            continue
        if 10 * both != 6 * D:          # 60% of D, exact integer check
            continue
        sols.append(dict(S_only=s_only, both=both, D_only=d_only, neither=20,
                         S=S, D=D, total=s_only + both + d_only + 20))
for s in sols:
    print(s)
assert len(sols) == 1 and sols[0]["total"] == 143
# formula view: 0.4|D| = 30 -> |D| = 75, both 45, |S| = 93, union = 93+75-45 = 123, +20 = 143
assert (sols[0]["D"], sols[0]["both"], sols[0]["S"]) == (75, 45, 93)

opts = {"A": 80, "B": 108, "C": 123, "D": 143}
matches = [k for k, v in opts.items() if v == sols[0]["total"]]
assert matches == ["D"], matches
print("note: 123 = union only, forgetting the 20 'neither' households (distractor C)")
print("ANSWER:", matches[0])
