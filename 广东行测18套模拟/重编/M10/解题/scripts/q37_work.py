"""M10 第37题：甲单独正好按计划T天完成；乙单独要T+5天；甲乙合作3天后乙单独做，正好T天完成。求T。
选项 A5 B7 C7.5 D8.5"""
from fractions import Fraction as F
opts = {'A': F(5), 'B': F(7), 'C': F(15, 2), 'D': F(17, 2)}
ok = []
for k, T in opts.items():
    total = F(1)
    ea, eb = total / T, total / (T + 5)
    done = 3 * (ea + eb) + (T - 3) * eb      # 乙全程T天，甲只做3天
    print(k, T, '按计划时间完成的工作量', done)
    if done == total:
        ok.append(k)
assert ok == ['C']
# 比例法：甲3天的量 = 乙5天的量，效率比5:3；总量5T=3(T+5) → T=7.5
T = F(3 * 5, 5 - 3)
assert T == F(15, 2)
print('效率比甲:乙=5:3，5T=3(T+5) → T =', T, '；答案：', ok)
