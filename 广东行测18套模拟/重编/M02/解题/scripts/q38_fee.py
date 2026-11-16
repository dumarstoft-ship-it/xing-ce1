"""第38题：线下人数=3×线上，线下收入=1.5×线上；共80人，总收入12万元，求线上单人报名费。
选项 A2400 B3600 C4000 D4800

核验：代数直接解 + 逐一代入选项检验总收入是否为 120000。
"""
from fractions import Fraction as F

online = F(80, 4)            # 线上 20 人
offline = 3 * online         # 线下 60 人
online_income = F(120000) / (1 + F(3, 2))   # 48000
fee_online = online_income / online
fee_offline = F(3, 2) * online_income / offline
print("线上人数", online, "线下人数", offline)
print("线上收入", online_income, "线上单价", fee_online, "线下单价", fee_offline)

options = {"A": 2400, "B": 3600, "C": 4000, "D": 4800}
for k, x in options.items():
    total = online * x + F(3, 2) * online * x
    print(k, x, "总收入", total, "符合" if total == 120000 else "")
