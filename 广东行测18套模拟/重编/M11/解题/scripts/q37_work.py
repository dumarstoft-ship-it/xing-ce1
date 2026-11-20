"""M11 第37题：两箱文件等量。小张4.5小时/箱、小钱9小时/箱、小周3小时/箱。小周先与小张整理第一箱，
小钱同时整理第二箱；后来小周转去与小钱一起，两箱同时完成。求小周与小张、与小钱一起的时间。
选项 A 1、2  B 1.5、1.5  C 2、1  D 1.2、1.8"""
from fractions import Fraction as F
box = F(9)                                   # 每箱赋值9
zhang, qian, zhou = box / F(9, 2), box / 9, box / 3   # 2、1、3
T = 2 * box / (zhang + qian + zhou)          # 三人始终都在干活，总时间
t1 = (box - zhang * T) / zhou                # 小周在第一箱的时间
t2 = T - t1
print('效率 张/钱/周 =', zhang, qian, zhou, '总时间', T, '小周：第一箱', t1, '第二箱', t2)
assert (t1, t2) == (1, 2)
assert zhang * T + zhou * t1 == box and qian * T + zhou * t2 == box
opts = {'A': (1, 2), 'B': (F(3, 2), F(3, 2)), 'C': (2, 1), 'D': (F(6, 5), F(9, 5))}
for k, (a, b) in opts.items():
    print(k, '第一箱完成', zhang * (a + b) + zhou * a, '第二箱完成', qian * (a + b) + zhou * b)
print('答案：', [k for k, (a, b) in opts.items() if zhang * (a + b) + zhou * a == box and qian * (a + b) + zhou * b == box])
