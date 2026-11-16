"""Q32: 8, 12, 23, 44, 78, ( )  options A99 B106 C128 D169"""
seq = [8, 12, 23, 44, 78]
opts = {"A": 99, "B": 106, "C": 128, "D": 169}

def diffs(s):
    return [s[i + 1] - s[i] for i in range(len(s) - 1)]

d1 = diffs(seq); d2 = diffs(d1); d3 = diffs(d2)
print("d1", d1, "d2", d2, "d3", d3)
assert d3 == [3, 3]
pred = seq[-1] + d1[-1] + d2[-1] + d3[-1]
print("predicted:", pred, "(d2 next 16, d1 next 50)")

# check every option: which makes the 3rd-level differences constant
ok = []
for k, v in opts.items():
    s = seq + [v]
    t = diffs(diffs(diffs(s)))
    print(k, v, "d3:", t)
    if len(set(t)) == 1:
        ok.append(k)
assert ok == ["C"], ok
print("ANSWER:", ok[0])
