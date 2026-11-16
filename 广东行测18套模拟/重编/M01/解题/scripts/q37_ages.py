"""Q37: family of four (dad, mom, Xiaoming, sister), total 100 this year.
dad = mom + 9, dad = 4 * xm; next year mom + 1 = 3 * (xm + 1). Find sister's age.
Brute force over integer ages."""
sols = []
for xm in range(0, 101):
    for mom in range(0, 101):
        dad = mom + 9
        if dad != 4 * xm:
            continue
        if mom + 1 != 3 * (xm + 1):
            continue
        sis = 100 - dad - mom - xm
        if sis >= 0:
            sols.append((dad, mom, xm, sis))
print("solutions (dad, mom, xiaoming, sister):", sols)
assert len(sols) == 1
dad, mom, xm, sis = sols[0]
assert sis < xm  # "妹妹" is younger than Xiaoming: consistent
opts = {"A": 9, "B": 10, "C": 11, "D": 12}
m = [k for k, v in opts.items() if v == sis]
print("ANSWER:", m[0])
