# 第34题：1，15，12，4，1，（ ）
# 规律：相邻两项之和 16、27、16、5、(1) 依次为 2^4、3^3、4^2、5^1、6^0。
seq = [1, 15, 12, 4, 1]
options = {"A": 0, "B": 1, "C": 2, "D": 3}
targets = [(n + 2) ** (4 - n) for n in range(5)]  # 2^4,3^3,4^2,5^1,6^0
print("目标和:", targets)
ok = []
for k, v in options.items():
    s = seq + [v]
    sums = [a + b for a, b in zip(s, s[1:])]
    fits = sums == targets
    print(k, v, "相邻和", sums, "符合" if fits else "")
    if fits:
        ok.append(k)
assert ok == ["A"], ok
print("答案:", ok, "；B=1 恰为 6^0 本身（忘记减去前一项1）")
