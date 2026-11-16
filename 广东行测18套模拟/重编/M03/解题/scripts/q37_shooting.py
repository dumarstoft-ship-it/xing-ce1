"""Q37: 10 shots, every shot is 7, 8 or 9; 8 is hit (strictly) most often; the total score is a
two-digit number whose tens and units digits are equal. How many 9s?   options A1 B2 C3 D4
Enumerate all (x7, y8, z9)."""
sols_all = []
for x in range(11):
    for y in range(11 - x):
        z = 10 - x - y
        total = 7 * x + 8 * y + 9 * z
        repdigit = 10 <= total <= 99 and total // 10 == total % 10
        if repdigit:
            sols_all.append((x, y, z, total))
print("all splits with a repdigit total:", sols_all)

strict = [s for s in sols_all if s[1] > s[0] and s[1] > s[2]]
print("8 strictly most:", strict)
weak = [s for s in sols_all if s[1] >= s[0] and s[1] >= s[2]]
print("8 most (ties allowed):", weak)
each_appears = [s for s in strict if min(s[:3]) >= 1]
print("8 strictly most and each of 7/8/9 hit at least once:", each_appears)

assert each_appears == [(4, 5, 1, 77)]
# Even allowing ties or zero 9s, the only extra case is (3,7,0) which has z=0 (not an option).
assert {s[2] for s in weak} == {0, 1}

opts = {"A": 1, "B": 2, "C": 3, "D": 4}
matches = [k for k, v in opts.items() if v == each_appears[0][2]]
assert matches == ["A"], matches
print("ANSWER:", matches[0])
