"""M05 第43题：三类项目夺冠概率 0.5、0.6、0.7（按相互独立处理），至少两类夺冠才获奖，求获奖概率。
枚举 2³=8 种结果。另算：若不假定独立，概率可在什么范围内变化（说明独立性是隐含前提）。
"""
from fractions import Fraction as F
from itertools import product

p = [F(1, 2), F(3, 5), F(7, 10)]
total = F(0)
for w in product([0, 1], repeat=3):
    pr = F(1)
    for wi, pi in zip(w, p):
        pr *= pi if wi else 1 - pi
    if sum(w) >= 2:
        print("夺冠组合", w, "概率", pr, float(pr))
        total += pr
print("至少两类夺冠概率:", total, "=", float(total))
assert total == F(13, 20)          # 0.65
assert F(6, 10) <= total < F(7, 10)

# 不假定独立时：给出两个边缘概率仍为0.5、0.6、0.7的联合分布，
# 获奖概率分别为0.4和0.9，说明"相互独立"是作答的隐含前提（按惯例默认独立）。
def marginals(joint):
    return [sum(pr for w, pr in joint.items() if w[i]) for i in range(3)]


low = {(1, 1, 1): F(2, 5), (1, 0, 0): F(1, 10), (0, 1, 0): F(1, 5), (0, 0, 1): F(3, 10)}
high = {(1, 1, 0): F(1, 5), (1, 0, 1): F(3, 10), (0, 1, 1): F(2, 5), (0, 0, 0): F(1, 10)}
for name, joint in (("低端", low), ("高端", high)):
    assert sum(joint.values()) == 1 and marginals(joint) == p
    pw = sum(pr for w, pr in joint.items() if sum(w) >= 2)
    print(f"不独立的{name}例：边缘概率{[str(x) for x in marginals(joint)]}，获奖概率 {pw} = {float(pw)}")
print("答案: C 60%-70%")
