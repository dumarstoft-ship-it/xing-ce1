# 第35题：9，45，54，57，58.5，（ ）
# 规律：一次作差 36、9、3、1.5，相邻差之商 4、3、2、(1)，下一差为1.5。
from fractions import Fraction as F
seq = [F(9), F(45), F(54), F(57), F(117, 2)]
options = {"A": F(117, 2), "B": F(59), "C": F(119, 2), "D": F(60)}
ok = []
for k, v in options.items():
    s = seq + [v]
    d = [b - a for a, b in zip(s, s[1:])]
    q = [d[i] / d[i + 1] if d[i + 1] != 0 else None for i in range(len(d) - 1)]
    fits = q == [4, 3, 2, 1]
    print(k, float(v), "差", [float(x) for x in d], "商", [None if x is None else float(x) for x in q], "符合" if fits else "")
    if fits:
        ok.append(k)
assert ok == ["D"], ok
print("答案:", ok)
