# 第33题：9，63，217，511，（ ）
# 规律：2^3+1，4^3-1，6^3+1，8^3-1，10^3+1。
seq = [9, 63, 217, 511]
options = {"A": 999, "B": 1001, "C": 1023, "D": 1025}
pattern = [(2 * (i + 1)) ** 3 + (1 if i % 2 == 0 else -1) for i in range(5)]
assert pattern[:4] == seq, pattern
print("幂次修正:", pattern)
ok = [k for k, v in options.items() if v == pattern[4]]
assert ok == ["B"], ok
# 干扰项对应的错误思路
print("C 1023 = 2^10-1 =", 2 ** 10 - 1, "（误以为 511=2^9-1、只看末两项）")
print("A 999 = 10^3-1 =", 10 ** 3 - 1, "（修正项 +1/-1 交替没看出）")
print("答案:", ok)
