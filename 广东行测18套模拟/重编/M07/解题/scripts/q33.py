# 第33题：28，16，30，38，53，（ ）  选项 A57 B61 C65 D72
from fractions import Fraction as F
seq = [28, 16, 30, 38, 53]
# 规律：第三项 = 第二项 + 第一项的一半
for i in range(2, len(seq)):
    pred = seq[i - 1] + F(seq[i - 2], 2)
    print(seq[i - 2], seq[i - 1], "→", pred, "实际", seq[i], pred == seq[i])
    assert pred == seq[i]
ans = seq[-1] + F(seq[-2], 2)
print("答案", ans)
opts = {"A": 57, "B": 61, "C": 65, "D": 72}
print([k for k, v in opts.items() if v == ans])
# 一级差 -12,14,8,15 无规律（作差走不通）
print("一级差", [b - a for a, b in zip(seq, seq[1:])])
