"""Q39: yi+bing together: 4 days.
jia 4 days then yi 5 days -> whole job.
jia alone does 1/4 of the job, then yi joins for 2 days, jia leaves, yi needs 3 more days -> done.
How many days for jia+bing together (round partial day up)?   options A3 B4 C5 D6"""
from fractions import Fraction as F
import math

# unknown efficiencies a (jia), b (yi), with job = 1:
#   4a + 5b = 1
#   1/4 + 2(a+b) + 3b = 1  ->  2a + 5b = 3/4
# subtract: 2a = 1/4
a = F(1, 8)
b = (1 - 4 * a) / 5
assert 2 * a + 5 * b == F(3, 4) and 4 * a + 5 * b == 1
c = F(1, 4) - b
print(f"jia {a}, yi {b}, bing {c} of the job per day")
assert (a, b, c) == (F(1, 8), F(1, 10), F(3, 20))

days = 1 / (a + c)
print(f"jia+bing per day = {a + c}; days = {days} = {float(days):.4f}; rounded up = {math.ceil(days)}")
assert days == F(40, 11) and math.ceil(days) == 4

# integer form: job = 40 -> jia 5, yi 4, bing 6, jia+bing 11
print("job 40 units: jia", a * 40, "yi", b * 40, "bing", c * 40)

opts = {"A": 3, "B": 4, "C": 5, "D": 6}
matches = [k for k, v in opts.items() if v == math.ceil(days)]
assert matches == ["B"], matches
print("ANSWER:", matches[0])
