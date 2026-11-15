# -*- coding: utf-8 -*-
"""Blind solve for Q43: 5 men, 4 women, 2 married couples; choose 2 men + 2 women uniformly.
P(exactly one couple among the chosen four)."""
from fractions import Fraction as F
from itertools import combinations, permutations
from math import comb

men = ["M1", "M2", "M3", "M4", "M5"]
women = ["W1", "W2", "W3", "W4"]

def count(couples):
    tot = ex1 = ex2 = ge1 = ex0 = 0
    for ms in combinations(men, 2):
        for ws in combinations(women, 2):
            tot += 1
            k = sum(1 for (m, w) in couples if m in ms and w in ws)
            ex0 += (k == 0); ex1 += (k == 1); ex2 += (k == 2); ge1 += (k >= 1)
    return tot, ex0, ex1, ex2, ge1

couples = [("M1", "W1"), ("M2", "W2")]
tot, ex0, ex1, ex2, ge1 = count(couples)
print("total selections:", tot, "(= C(5,2)*C(4,2) =", comb(5, 2) * comb(4, 2), ")")
print("exactly 0 couples:", ex0, F(ex0, tot))
print("exactly 1 couple :", ex1, F(ex1, tot))
print("exactly 2 couples:", ex2, F(ex2, tot))
print("at least 1 couple:", ge1, F(ge1, tot))

# robustness: every way of placing 2 disjoint man-woman couples gives the same count
vals = set()
for m_pair in permutations(men, 2):
    for w_pair in permutations(women, 2):
        cs = [(m_pair[0], w_pair[0]), (m_pair[1], w_pair[1])]
        vals.add(count(cs)[2])
print("exactly-1 count over all couple placements:", vals)

# formula check
formula = 2 * (comb(4, 1) * comb(3, 1) - 1)
print("formula 2*(C(4,1)*C(3,1)-1) =", formula, "->", F(formula, 60))

options = {"A": F(9, 20), "B": F(2, 5), "C": F(13, 30), "D": F(11, 30)}
print("\noptions as /60:", {k: v * 60 for k, v in options.items()})
print("matching option:", [k for k, v in options.items() if v == F(ex1, tot)])
print("\nerror paths:")
print("  2*C(4,1)*C(3,1)/60 (forgot to remove the both-couples case) =", F(2 * 4 * 3, 60))
print("  inclusion-exclusion 'at least one' =", F(2 * 4 * 3 - 1, 60))
# other conceivable slips
print("  2*C(3,1)*C(2,1)/60 (other man/woman both from non-couple people only) =", F(2 * 3 * 2, 60))
print("  choose 4 of 9 freely, exactly 1 couple:",
      F(sum(1 for s in combinations(men + women, 4)
            if sum(1 for (m, w) in couples if m in s and w in s) == 1), comb(9, 4)))
