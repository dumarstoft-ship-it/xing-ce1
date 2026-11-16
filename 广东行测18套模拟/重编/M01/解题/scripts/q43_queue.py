"""Q43: 8 people in a queue (甲 乙 丙 丁 + 4 others). 甲 and 乙 are not at either end and are
adjacent; 丙 and 丁 are each adjacent to neither 甲 nor 乙. Brute force over 8! orders."""
from itertools import permutations
people = ["J", "Y", "B", "D", "o1", "o2", "o3", "o4"]   # J=甲 Y=乙 B=丙 D=丁
cnt = 0
for perm in permutations(people):
    pos = {p: i for i, p in enumerate(perm)}
    j, y = pos["J"], pos["Y"]
    if j in (0, 7) or y in (0, 7):
        continue
    if abs(j - y) != 1:
        continue
    bad = False
    for x in ("B", "D"):
        if abs(pos[x] - j) == 1 or abs(pos[x] - y) == 1:
            bad = True
    if bad:
        continue
    cnt += 1
print("count =", cnt, " formula 5*2*A(4,2)*4! =", 5 * 2 * 12 * 24)
opts = {"A": 5760, "B": 4210, "C": 2880, "D": 1440}
m = [k for k, v in opts.items() if v == cnt]
assert m == ["C"], m
print("ANSWER:", m[0])
