"""Q43: 3 boys + 5 girls (8 distinct people). Roles: 1 host (must be a girl), 3 keep order,
4 hand out prizes; everyone does exactly one job. Among the 4 prize presenters, girls >= boys.
How many arrangements?   options A260 B155 C150 D65
Brute force over every way to split the 8 people into the three groups."""
from itertools import combinations
from math import comb

people = [("B", i) for i in range(3)] + [("G", i) for i in range(5)]
count = 0
count_strict = 0
for host in people:
    if host[0] != "G":
        continue
    rest = [p for p in people if p != host]
    for award in combinations(rest, 4):
        g = sum(1 for p in award if p[0] == "G")
        b = 4 - g
        # the remaining 3 automatically keep order
        if g >= b:
            count += 1
        if g > b:
            count_strict += 1
print("girls >= boys among presenters:", count)
print("(if misread as girls > boys:", count_strict, ")")
assert count == 155 and count_strict == 65

# formula: 5 * [C(4,2)C(3,2) + C(4,3)C(3,1) + C(4,4)] = 5 * (18 + 12 + 1)
assert 5 * (comb(4, 2) * comb(3, 2) + comb(4, 3) * comb(3, 1) + comb(4, 4)) == 155
# complement: 5 * [C(7,4) - C(4,1)C(3,3)] = 5 * (35 - 4)
assert 5 * (comb(7, 4) - comb(4, 1) * comb(3, 3)) == 155

opts = {"A": 260, "B": 155, "C": 150, "D": 65}
matches = [k for k, v in opts.items() if v == count]
assert matches == ["B"], matches
print("ANSWER:", matches[0])
