"""Q31: 19, -15, 24, 1, 48, ( )  options A63 B73 C81 D92
Hypothesis: sums of adjacent terms are squares of consecutive primes 2,3,5,7,11."""
from math import isqrt

seq = [19, -15, 24, 1, 48]
opts = {"A": 63, "B": 73, "C": 81, "D": 92}

sums = [seq[i] + seq[i + 1] for i in range(len(seq) - 1)]
print("adjacent sums:", sums, "roots:", [isqrt(s) for s in sums],
      "all squares:", all(isqrt(s) ** 2 == s for s in sums))

primes = [2, 3, 5, 7, 11, 13]
assert sums == [p * p for p in primes[:4]]
pred = primes[4] ** 2 - seq[-1]
print("predicted next = 11^2 - 48 =", pred)

for k, v in opts.items():
    s = seq[-1] + v
    print(k, v, "48+x =", s, "square" if isqrt(s) ** 2 == s else "not square")

# plain differences for contrast (no clean pattern)
print("differences:", [seq[i + 1] - seq[i] for i in range(len(seq) - 1)])
matches = [k for k, v in opts.items() if v == pred]
assert matches == ["B"], matches
print("ANSWER:", matches[0])
