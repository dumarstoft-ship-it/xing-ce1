"""第31题：3，2，√13，8，6，10，10，3，（ ）
三个一组：(3,2,√13)、(8,6,10)、(10,3,?)，检验 第一项² + 第二项² = 第三项²。
"""
import math

groups = [(3, 2, math.sqrt(13)), (8, 6, 10)]
for a, b, c in groups:
    print(f"({a},{b},{c:.4f}): a^2+b^2={a*a+b*b}, c^2={c*c:.4f}", "OK" if abs(a * a + b * b - c * c) < 1e-9 else "FAIL")

options = {"A": math.sqrt(109), "B": 11, "C": math.sqrt(103), "D": 109}
a, b = 10, 3
target = math.sqrt(a * a + b * b)
print("预测第三组第三项 = sqrt(10^2+3^2) = sqrt(%d) = %.4f" % (a * a + b * b, target))
hits = [k for k, v in options.items() if abs(v - target) < 1e-9]
print("吻合选项:", hits)

# 排除其他分组/规律：若按 a+b 或 a*b 关系，均不吻合前两组
for name, f in [("a+b", lambda a, b: a + b), ("a*b", lambda a, b: a * b), ("a^2-b^2", lambda a, b: a * a - b * b)]:
    ok = all(abs(f(a_, b_) - c_) < 1e-9 for a_, b_, c_ in groups)
    print(f"规律 {name} 是否吻合前两组: {ok}")
assert hits == ["A"]
