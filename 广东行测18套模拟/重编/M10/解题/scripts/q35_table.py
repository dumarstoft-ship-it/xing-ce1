"""M10 第35题：数表（原卷2022年县级卷第28题题图，已看图核对）
 1  2  3
 2  5 10
 3 10 29
 4 17 （ ）   选项 A62 B64 C66 D68
规律：每行 a、a²+1、a³+2。"""
import itertools
rows = [(1, 2, 3), (2, 5, 10), (3, 10, 29)]
opts = {'A': 62, 'B': 64, 'C': 66, 'D': 68}
for a, b, c in rows:
    assert b == a ** 2 + 1 and c == a ** 3 + 2
a, b = 4, 17
assert b == a ** 2 + 1
ans = a ** 3 + 2
print('第4行：', a, b, ans)
# 另一写法：第3列 = 第1列×第2列 − 第1列 + 2
assert all(c == a_ * b_ - a_ + 2 for a_, b_, c in rows)
assert a * b - a + 2 == ans
# 穷举 c = p·a·b + q·a² + r·b + s·a + t（系数−3…3）中拟合前三行的规律给出的值
vals = {}
R = range(-3, 4)
for p, q, r, s, t in itertools.product(R, R, R, R, R):
    f = lambda a_, b_: p * a_ * b_ + q * a_ * a_ + r * b_ + s * a_ + t
    if all(c == f(a_, b_) for a_, b_, c in rows):
        vals.setdefault(f(a, b), 0)
        vals[f(a, b)] += 1
print('同类线性组合拟合前三行后给出的第4行值：', vals)
print('答案：', [k for k, v in opts.items() if v == ans])
