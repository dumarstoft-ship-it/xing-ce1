"""Q35 table (rows): 12 4 64 / 25 19 36 / 40 31 81 / 17 12 ?   options A121 B49 C25 D9
Search a set of simple two-argument rules g(a,b)+k (k fixed by row 1) and keep the ones
that fit rows 1-3, then see what each predicts for row 4."""
rows = [(12, 4, 64), (25, 19, 36), (40, 31, 81)]
last = (17, 12)
opts = {"A": 121, "B": 49, "C": 25, "D": 9}

base = {
    "(a-b)^2": lambda a, b: (a - b) ** 2,
    "(a+b)^2": lambda a, b: (a + b) ** 2,
    "a^2-b^2": lambda a, b: a * a - b * b,
    "a*b": lambda a, b: a * b,
    "a+b": lambda a, b: a + b,
    "2a-b": lambda a, b: 2 * a - b,
    "(a-b)^3": lambda a, b: (a - b) ** 3,
    "a^2/b": lambda a, b: a * a / b,
}
fits = {}
for name, g in base.items():
    k = rows[0][2] - g(*rows[0][:2])
    if all(g(a, b) + k == c for a, b, c in rows):
        fits[f"{name}{'+' + str(k) if k else ''}"] = g(*last) + k
print("rules fitting rows 1-3 ->", fits)
for a, b, c in rows + [(17, 12, "?")]:
    print(a, b, " a-b =", a - b, " (a-b)^2 =", (a - b) ** 2, " given:", c)
assert set(fits.values()) == {25}
matches = [k for k, v in opts.items() if v == 25]
assert matches == ["C"]
print("ANSWER:", matches[0])
