"""Q32: 12, 18, 29, 46, 70, ( )   options A102 B103 C104 D105
First differences, then second differences; the second differences form 5, 6, 7 -> 8."""
seq = [12, 18, 29, 46, 70]
opts = {"A": 102, "B": 103, "C": 104, "D": 105}

d1 = [b - a for a, b in zip(seq, seq[1:])]
d2 = [b - a for a, b in zip(d1, d1[1:])]
print("1st diff:", d1)
print("2nd diff:", d2)
assert d2 == [5, 6, 7]
next_d2 = d2[-1] + 1
next_d1 = d1[-1] + next_d2
pred = seq[-1] + next_d1
print(f"next 2nd diff {next_d2}, next 1st diff {next_d1}, next term {pred}")

# Check a competing idea: d1 as a 'sum of previous two' recursion (6+11=17 but 11+17=28!=24)
print("d1 'sum of previous two'?", [d1[i] + d1[i + 1] == d1[i + 2] for i in range(len(d1) - 2)])

matches = [k for k, v in opts.items() if v == pred]
assert matches == ["A"], matches
for k, v in opts.items():
    dd = v - seq[-1]
    print(k, v, "-> last 1st diff", dd, ", last 2nd diff", dd - d1[-1])
print("ANSWER:", matches[0])
