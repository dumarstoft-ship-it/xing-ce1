"""第35题：四个圆，每圆四格（左上TL、右上TR、左下BL、右下BR），求第4圆右下。
题图原图（s19_p10_i04）不在 assets 中，按题面转写表作答。
规律：TR × BL − TL = BR。
另外在一个小的候选式族中搜索所有能同时拟合前三个圆的式子，看它们对第4圆的预测是否都落在同一选项。
"""
from itertools import permutations, product

circles = [(25, 3, 7, -4), (14, 8, 6, 34), (51, 9, 4, -15)]
last = (22, 8, 7)
options = {"A": 23, "B": 34, "C": 45, "D": 56}

for tl, tr, bl, br in circles:
    print(f"{tr}×{bl}−{tl} = {tr*bl - tl}  实际 {br}")
    assert tr * bl - tl == br
pred = last[1] * last[2] - last[0]
print("第4圆：8×7−22 =", pred)

# 候选式族：BR = s1*x*y + s2*z + c 及 BR = s1*x + s2*y + s3*z + c 等，x,y,z 为三格的任意排列
names = ["TL", "TR", "BL"]
fits = {}
for perm in permutations(range(3)):
    for s1, s2 in product((1, -1), repeat=2):
        for c in range(-10, 11):
            f = lambda v, perm=perm, s1=s1, s2=s2, c=c: s1 * v[perm[0]] * v[perm[1]] + s2 * v[perm[2]] + c
            if all(f(cir[:3]) == cir[3] for cir in circles):
                expr = f"{'+' if s1>0 else '-'}{names[perm[0]]}*{names[perm[1]]} {'+' if s2>0 else '-'} {names[perm[2]]} {c:+d}"
                fits[expr] = f(last)
    for s in product((1, -1, 2, -2, 3, -3), repeat=3):
        for c in range(-10, 11):
            g = lambda v, s=s, c=c: s[0] * v[0] + s[1] * v[1] + s[2] * v[2] + c
            if all(g(cir[:3]) == cir[3] for cir in circles):
                fits[f"linear {s} {c:+d}"] = g(last)
print("能拟合前三圆的式子及其预测:")
for k, v in fits.items():
    print("  ", k, "->", v)
preds = set(fits.values())
print("预测值集合:", preds)
hits = [k for k, v in options.items() if v == pred]
assert hits == ["B"]
print("答案:", hits)
