"""Q34: 63, 5, 58, 12, 46, 8, 38, 20, ( )  options A19 B16 C21 D18
Odd-position terms: each = previous odd term minus the even term between them."""
seq = [63, 5, 58, 12, 46, 8, 38, 20]
opts = {"A": 19, "B": 16, "C": 21, "D": 18}

odd = seq[0::2]; even = seq[1::2]
print("odd positions:", odd, "even positions:", even)
for i in range(len(odd) - 1):
    print(f"{odd[i]} - {even[i]} = {odd[i]-even[i]}  (actual {odd[i+1]})")
    assert odd[i] - even[i] == odd[i + 1]
# the same relation seen as a(2k+1) = a(2k-1) - a(2k); it does NOT hold for even terms:
print("even-position check a4 = a2 - a3 ?", seq[1] - seq[2], "vs", seq[3])
pred = odd[-1] - even[-1]
print("predicted: 38 - 20 =", pred)
matches = [k for k, v in opts.items() if v == pred]
assert matches == ["D"], matches
print("ANSWER:", matches[0])
