"""M08 第42题：每次投篮随机选球，P(专业)-P(普通)=20个百分点；普通球命中40%，专业球60%。求连投3次均中概率所在区间。"""
from fractions import Fraction as F
import random
pn, pp = F(2, 5), F(3, 5)       # 选普通/专业球的概率：pp-pn=0.2, pp+pn=1
hit = pn*F(2, 5) + pp*F(3, 5)
p3 = hit**3
print('单次命中率', hit, float(hit), '  连中3次', p3, float(p3))
ranges = {'A': (0.20, 0.24), 'B': (0.16, 0.20), 'C': (0.12, 0.16), 'D': (0.10, 0.12)}
ans = [k for k, (lo, hi) in ranges.items() if lo <= float(p3) <= hi]
print('落入区间:', ans); assert ans == ['C']
# 其它读法也都落在C：只选一次球、三次都用它
once = pn*F(2, 5)**3 + pp*F(3, 5)**3
print('若3次共用一次选择:', float(once))
# 模拟
random.seed(1); n = 400000; c = 0
for _ in range(n):
    c += all(random.random() < (0.6 if random.random() < 0.6 else 0.4) for _ in range(3))
print('蒙特卡洛', c/n)
print('误只用专业球 0.6^3 =', 0.6**3, '→ 落入A区间')
