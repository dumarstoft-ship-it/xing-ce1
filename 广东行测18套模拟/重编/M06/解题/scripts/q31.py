# 第31题：2，5，3，7，2，11，12，（ ）
# 规律：两两分组，组内求和 7、10、13、(16)，公差为3的等差数列。
seq = [2, 5, 3, 7, 2, 11, 12]
options = {"A": 2, "B": 3, "C": 4, "D": 5}

def pair_sums(s):
    return [s[i] + s[i + 1] for i in range(0, len(s), 2)]

ok = []
for k, v in options.items():
    sums = pair_sums(seq + [v])
    diffs = [b - a for a, b in zip(sums, sums[1:])]
    fits = len(set(diffs)) == 1
    print(k, v, "组内和", sums, "差", diffs, "符合" if fits else "")
    if fits:
        ok.append(k)
assert ok == ["C"], ok

# 排查其他常见规律是否也能给出某个选项
odd, even = seq[0::2], seq[1::2]
print("奇数项", odd, "偶数项", even)  # 2,3,2,12 / 5,7,11 无单独规律
print("两两之积", [seq[i] * seq[i + 1] for i in range(0, 6, 2)])  # 10,21,22 无规律
print("答案:", ok)
