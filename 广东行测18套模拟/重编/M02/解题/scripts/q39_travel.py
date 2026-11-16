"""第39题：甲乙相距500米，小吴(0.5米/秒)从甲、小赵从乙相向出发，在丙相遇；
相遇后小赵掉头提速60%，4分钟后回到乙。求小吴从丙到乙用时。

核验：设小赵原速 v，丙乙距离 d=v*t=1.6v*240 => 相遇用时 t=384 秒；
再用精确分数计算，并用数值模拟复核。
"""
from fractions import Fraction as F

wu = F(1, 2)
back_time = F(240)                  # 4 分钟
t_meet = F(16, 10) * back_time      # d = v*t = 1.6v*240  ->  t = 384
d_wu = wu * t_meet                  # 小吴到丙走了 192 米
d_cb = 500 - d_wu                   # 丙到乙 308 米
v_zhao = d_cb / t_meet              # 小赵原速
t_wu = d_cb / wu
print("相遇用时", t_meet, "秒；甲丙", d_wu, "米；丙乙", d_cb, "米")
print("小赵原速", v_zhao, "≈", float(v_zhao), "米/秒；提速后", float(F(16, 10) * v_zhao))
print("检验：小赵返程用时", d_cb / (F(16, 10) * v_zhao), "秒")
print("小吴丙到乙用时", t_wu, "秒 =", float(t_wu / 60), "分钟")

m = float(t_wu / 60)
if m < 11:
    ans = "A 在11分钟之内"
elif m < 13:
    ans = "B 11-13分钟"
elif m < 15:
    ans = "C 13-15分钟"
else:
    ans = "D 15分钟以上"
print("对应选项", ans)
