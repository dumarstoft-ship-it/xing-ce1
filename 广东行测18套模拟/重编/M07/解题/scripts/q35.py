# 第35题：表格数阵
# 2 2 5 / 3 5 19 / 4 7 37 / 5 11 ?   选项 A46 B55 C71 D83
rows = [(2, 2, 5), (3, 5, 19), (4, 7, 37)]
f = lambda a, b: a * b + (a - 1) ** 2      # 等价于 a(a+b-2)+1
for a, b, c in rows:
    print(a, b, c, "ab=", a * b, "c-ab=", c - a * b, "(a-1)^2=", (a - 1) ** 2, f(a, b) == c)
    assert f(a, b) == c
ans = f(5, 11)
print("答案", ans)
opts = {"A": 46, "B": 55, "C": 71, "D": 83}
print([k for k, v in opts.items() if v == ans])
# 其他尝试：c-2ab = -3,-11,-19（每次-8）→ 第四行 110-27=83（D），属于按行号凑出的规律，不如行内运算统一
print("2ab-c:", [2 * a * b - c for a, b, c in rows], "→ 若继续-8：", 2 * 5 * 11 - 27)
print("只算乘积 ab =", 5 * 11, "(B)")
# 小范围穷举：c = p*a^2 + q*b^2 + r*ab + s*a + t*b + u（系数-2..2，常数-3..3）中，三行全符合的公式各给出什么答案
from itertools import product
from collections import Counter
cnt = Counter()
for p, q, r, s, t, u in product(range(-2, 3), range(-2, 3), range(-2, 3), range(-2, 3), range(-2, 3), range(-3, 4)):
    g = lambda a, b: p * a * a + q * b * b + r * a * b + s * a + t * b + u
    if all(g(a, b) == c for a, b, c in rows):
        cnt[g(5, 11)] += 1
        if sum(map(abs, (p, q, r, s, t, u))) <= 5:
            print("简单公式", (p, q, r, s, t, u), "→", g(5, 11))
print("所有符合的二次式给出的第四行值（值:个数）", dict(cnt))
