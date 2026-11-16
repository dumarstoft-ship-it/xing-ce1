"""Q40: 4 boys (incl. Li) and 3 girls (incl. Zhang), choose 3; at least one boy and one girl;
exactly one of Li and Zhang is chosen. Enumerate all 3-subsets."""
from itertools import combinations
boys = ["Li", "B2", "B3", "B4"]
girls = ["Zhang", "G2", "G3"]
people = boys + girls
cnt = 0; case_li = case_zh = 0
for c in combinations(people, 3):
    nb = sum(p in boys for p in c); ng = 3 - nb
    if nb < 1 or ng < 1:
        continue
    li, zh = "Li" in c, "Zhang" in c
    if li == zh:          # need exactly one of them
        continue
    cnt += 1
    case_li += li; case_zh += zh
print("Li in, Zhang out:", case_li, "(= C(5,2)-C(3,2) = 10-3)")
print("Zhang in, Li out:", case_zh, "(= C(5,2)-C(2,2) = 10-1)")
print("total:", cnt)
opts = {"A": 16, "B": 17, "C": 18, "D": 19}
m = [k for k, v in opts.items() if v == cnt]
assert m == ["A"], m
print("ANSWER:", m[0])
