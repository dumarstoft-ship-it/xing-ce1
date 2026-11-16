# 第43题：设骑完 A→B 全程需 T 分钟（骑行速度 v），开车 5v 需 T/5 分钟
from fractions import Fraction as F
for T in range(61, 400):
    jia = T + 20                       # 甲：骑行 T 分钟 + 休息 20 分钟
    yi = 60 + 20 + 60 + F(T, 5)        # 乙：同行 60 + 休息 20 + 原速返回 60 + 开车 T/5
    if jia - yi == 12:
        print('T =', T, '甲全程 =', jia, '分钟；乙 =', yi, '分钟；差 =', jia - yi)
