"""M06换入的数字推理复算：第32题（JS2020-A类-048，递推）、第35题（JS2020-A类-050，分数数列）。"""
from fractions import Fraction as F

# 第32题：3，7，16，36，80，（ ）：后项＝前项×2＋修正项，修正项1、2、4、8、16
a = [3, 7, 16, 36, 80]
corr = [a[i + 1] - 2 * a[i] for i in range(4)]
assert corr == [1, 2, 4, 8]
nxt = 2 * a[-1] + 2 * corr[-1]
print("第32题 修正项", corr, "→ 下一项", nxt)
assert nxt == 176                       # A
d1 = [a[i + 1] - a[i] for i in range(4)]
print("  作差", d1, "（4、9、20、44，后一个差＝前一个差×2＋1、2、4，与递推同一规律）")

# 第35题：32/7，4，128/25，128/17，512/43，（ ）：反约分后分子32、64、128、256、512，分母7、16、25、34、43
terms = [F(32, 7), F(4), F(128, 25), F(128, 17), F(512, 43)]
nums = [32 * 2 ** i for i in range(5)]
dens = [7 + 9 * i for i in range(5)]
assert all(F(n, d) == t for n, d, t in zip(nums, dens, terms))
ans = F(nums[-1] * 2, dens[-1] + 9)
print("第35题 反约分", [f"{n}/{d}" for n, d in zip(nums, dens)], "→", f"{nums[-1]*2}/{dens[-1]+9}", "=", ans)
assert ans == F(256, 13)                # B
opts = {"A": F(6), "B": F(256, 13), "C": F(512, 19), "D": F(512, 53)}
print("  选项", {k: float(v) for k, v in opts.items()}, "；1024/52约分为256/13，只有B")
