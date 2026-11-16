"""Q34: 4/3, 1, 6/7, 7/9, 8/11, ( )   options A 3/4  B 5/6  C 9/13  D 10/13
Write 1 as 5/5: numerators 4,5,6,7,8 (+1 each), denominators 3,5,7,9,11 (+2 each)."""
from fractions import Fraction as F

nums = [4, 5, 6, 7, 8]
dens = [3, 5, 7, 9, 11]
given = [F(4, 3), F(1), F(6, 7), F(7, 9), F(8, 11)]
assert [F(n, d) for n, d in zip(nums, dens)] == given
assert all(b - a == 1 for a, b in zip(nums, nums[1:]))
assert all(b - a == 2 for a, b in zip(dens, dens[1:]))

pred = F(nums[-1] + 1, dens[-1] + 2)
print("predicted:", pred)
opts = {"A": F(3, 4), "B": F(5, 6), "C": F(9, 13), "D": F(10, 13)}
matches = [k for k, v in opts.items() if v == pred]
assert matches == ["C"], matches

# Values decrease monotonically; the predicted term continues that, D (10/13 = 0.769) breaks
# the numerator step and is a distractor built from the same denominator.
print("values:", [round(float(x), 4) for x in given + [pred]])
print("ANSWER:", matches[0])
