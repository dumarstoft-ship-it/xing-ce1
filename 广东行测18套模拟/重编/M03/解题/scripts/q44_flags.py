"""Q44: both sides of a street; flags every 8 m with flags at both ends. A stage is built at the
far end and no flags within 144 m of it. Keep the flag count, re-space to 6 m with flags at the
(new) start and end. How many flags do not move?   options A19 B38 C36 D50"""
from fractions import Fraction as F

# per side: L/8 + 1 = (L - 144)/6 + 1  ->  6L = 8L - 1152  ->  L = 576
L = F(1152, 2)
assert L / 8 == (L - 144) / 6
L = int(L)
old = set(range(0, L + 1, 8))
new = set(range(0, L - 144 + 1, 6))
print(f"street length {L} m; per side old {len(old)} flags, new {len(new)} flags")
assert len(old) == len(new) == 73

# brute force on length: only L = 576 keeps the count equal (L a multiple of 8, L-144 of 6)
Ls = [x for x in range(152, 5000, 8) if (x - 144) % 6 == 0 and x // 8 + 1 == (x - 144) // 6 + 1]
print("lengths that keep the count:", Ls)
assert Ls == [576]

stay = sorted(old & new)
print("unmoved per side:", len(stay), "positions", stay[:4], "...", stay[-2:])
assert len(stay) == 19 and stay == list(range(0, 433, 24))
both_sides = 2 * len(stay)
print("both sides:", both_sides)

opts = {"A": 19, "B": 38, "C": 36, "D": 50}
matches = [k for k, v in opts.items() if v == both_sides]
assert matches == ["B"], matches
print("note: 19 = one side only (distractor A)")
print("ANSWER:", matches[0])
