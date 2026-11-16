"""M05 第34题：5，18，16，29，27，40，38，（ ）

思路：相邻两项交替 +13、−2；等价于奇数项 5,16,27,38 与偶数项 18,29,40 都是公差11的等差数列。
"""
seq = [5, 18, 16, 29, 27, 40, 38]
options = {"A": 48, "B": 49, "C": 50, "D": 51}

d = [b - a for a, b in zip(seq, seq[1:])]
print("相邻差:", d)
assert d == [13, -2] * 3

odd, even = seq[0::2], seq[1::2]
print("奇数项:", odd, "偶数项:", even)
assert all(b - a == 11 for a, b in zip(odd, odd[1:]))
assert all(b - a == 11 for a, b in zip(even, even[1:]))

hits = []
for k, v in options.items():
    s = seq + [v]
    ev = s[1::2]
    ok = all(b - a == 11 for a, b in zip(ev, ev[1:])) and s[-1] - s[-2] == 13
    print(f"{k} {v}: {'符合' if ok else '不符'}")
    if ok:
        hits.append(k)
assert hits == ["D"], hits
print("答案: D 51")
