"""Q45: yi(+2 years) = bing(-4 years); 2 years ago bing was twice jia; in 2 years the three ages
sum to 131. How many years ago was yi + bing = 4 x jia?   options A2 B3 C4 D5
Brute force on current ages."""
sols = []
for jia in range(1, 121):
    for yi in range(1, 121):
        for bing in range(1, 121):
            if yi + 2 == bing - 4 and bing - 2 == 2 * (jia - 2) and jia + yi + bing + 6 == 131:
                sols.append((jia, yi, bing))
print("current ages (jia, yi, bing):", sols)
assert sols == [(27, 46, 52)]
jia, yi, bing = sols[0]

ns = [n for n in range(0, jia) if (yi - n) + (bing - n) == 4 * (jia - n)]
print("years ago with yi+bing = 4*jia:", ns)
assert ns == [5]
n = ns[0]
print(f"{n} years ago: jia {jia-n}, yi {yi-n}, bing {bing-n}; {yi-n}+{bing-n} = {yi+bing-2*n} = 4 x {jia-n}")

opts = {"A": 2, "B": 3, "C": 4, "D": 5}
matches = [k for k, v in opts.items() if v == n]
assert matches == ["D"], matches
print("ANSWER:", matches[0])
