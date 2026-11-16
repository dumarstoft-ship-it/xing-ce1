# 第67题：弹簧上放2m的A，长l1；再放m的B，长l2。求原长L0与劲度系数k。
# 平衡：k(L0-l1)=2mg，k(L0-l2)=3mg  =>  k=mg/(l1-l2)，L0=3l1-2l2。
# 用几组数值代入，检验四个选项哪一个同时满足两式。
from fractions import Fraction as F

options = {
    "A": (lambda l1, l2: 3 * l1 - 2 * l2, lambda m, g, l1, l2: m * g / (l1 - l2)),
    "B": (lambda l1, l2: 3 * l2 - 2 * l1, lambda m, g, l1, l2: m * g / (l1 - l2)),
    "C": (lambda l1, l2: 3 * l1 - 2 * l2, lambda m, g, l1, l2: 2 * m * g / (l1 - l2)),
    "D": (lambda l1, l2: 3 * l2 - 2 * l1, lambda m, g, l1, l2: 2 * m * g / (l1 - l2)),
}
hits = set("ABCD")
for m, g, k, L0 in [(F(1), F(10), F(200), F(1)), (F(3, 2), F(98, 10), F(500), F(7, 5)), (F(2), F(10), F(80), F(2))]:
    l1 = L0 - 2 * m * g / k
    l2 = L0 - 3 * m * g / k
    assert l1 > l2 > 0
    ok = {key for key, (fL, fk) in options.items() if fL(l1, l2) == L0 and fk(m, g, l1, l2) == k}
    print("m=%s g=%s k=%s L0=%s -> l1=%s l2=%s 满足:%s" % (m, g, k, L0, l1, l2, sorted(ok)))
    hits &= ok
assert hits == {"A"}
print("答案: A（C把k写成2mg/(l1-l2)，是把只放A时的弹力2mg误当作长度变化l1-l2对应的力）")
