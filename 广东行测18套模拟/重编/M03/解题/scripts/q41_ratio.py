"""Q41: fewer than 100 staff; switchers = 15/26 of all; among switchers women = 1.25 x men;
overall men:women = 7:6. How many men do NOT switch?   options A20 B22 C24 D26
Enumerate every head count and every split of switchers."""
sols = []
for n in range(1, 100):
    if (15 * n) % 26 or (7 * n) % 13:
        continue
    men, women = 7 * n // 13, 6 * n // 13
    sw = 15 * n // 26
    for m_sw in range(0, sw + 1):
        w_sw = sw - m_sw
        if 4 * w_sw == 5 * m_sw and m_sw <= men and w_sw <= women:
            sols.append(dict(n=n, men=men, women=women, switch=sw, men_sw=m_sw, women_sw=w_sw,
                             men_stay=men - m_sw, women_stay=women - w_sw))
for s in sols:
    print(s)
assert len(sols) == 1 and sols[0]["n"] == 78 and sols[0]["men_stay"] == 22

opts = {"A": 20, "B": 22, "C": 24, "D": 26}
matches = [k for k, v in opts.items() if v == sols[0]["men_stay"]]
assert matches == ["B"], matches
print("note: 20 = men who switch (distractor A)")
print("ANSWER:", matches[0])
