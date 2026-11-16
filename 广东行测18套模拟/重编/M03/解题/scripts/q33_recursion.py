"""Q33: 3, 7, 23, 95, 479, ( )   options A2877 B2879 C2883 D2885
Pattern: a(k+1) = (k+1)*a(k) + k, i.e. (a(k+1)+1) = (k+1)*(a(k)+1).
Each term +1 gives 4, 8, 24, 96, 480 with ratios 2, 3, 4, 5 -> next ratio 6."""
from fractions import Fraction as F

seq = [3, 7, 23, 95, 479]
opts = {"A": 2877, "B": 2879, "C": 2883, "D": 2885}

for k in range(1, len(seq)):
    a, b = seq[k - 1], seq[k]
    print(f"{a} x {k+1} + {k} = {a*(k+1)+k}  (actual {b})")
    assert a * (k + 1) + k == b

plus1 = [x + 1 for x in seq]
ratios = [F(b, a) for a, b in zip(plus1, plus1[1:])]
print("terms+1:", plus1, " ratios:", [str(r) for r in ratios])
assert ratios == [2, 3, 4, 5]

pred = seq[-1] * 6 + 5
print("predicted: 479 x 6 + 5 =", pred)

# Second view: differences 4, 16, 72, 384 = 4*1!, 8*2!, 12*3!, 16*4! -> next 20*5! = 2400
d = [b - a for a, b in zip(seq, seq[1:])]
import math
print("differences:", d, " = ", [f"{4*(i+1)}*{i+1}!" for i in range(4)])
assert d == [4 * (i + 1) * math.factorial(i + 1) for i in range(4)]
assert seq[-1] + 20 * math.factorial(5) == pred

for k, v in opts.items():
    print(k, v, "(x+1)/480 =", F(v + 1, 480))
matches = [k for k, v in opts.items() if v == pred]
assert matches == ["B"], matches
print("ANSWER:", matches[0])
