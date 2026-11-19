"""M09 第37题：牛吃草。20头牛20天吃光；10牛+10羊30天吃光；1牛=2羊。30只羊几天吃光？ 选项 A10 B20 C30 D40
核验：设1只羊每天吃1份，1头牛2份；原有草量Y、每天长草r：
  (40−r)×20 = Y，(30−r)×30 = Y → r=10，Y=600；30只羊：600÷(30−10)=30天。
再按天数枚举，确认只有30天满足。"""
from fractions import Fraction as F
# 解方程
r = F(40 * 20 - 30 * 30, 20 - 30)
Y = 40 * 20 - 20 * r
print('每天长草 r =', r, '原有草量 Y =', Y)
assert (40 - r) * 20 == Y == (30 - r) * 30
T = Y / (30 - r)
print('30只羊所需天数 T =', T)
opts = {'A': 10, 'B': 20, 'C': 30, 'D': 40}
ok = [k for k, v in opts.items() if (30 - r) * v == Y]
assert ok == ['C'] and T == 30
# 逐日模拟（离散检验）：第t天末剩余草量
grass = Y
for t in range(1, 41):
    grass += r - 30
    if grass <= 0:
        print('逐日模拟：第', t, '天吃光')
        break
# 易错：忘记草在生长，直接600÷30
print('忽略长草：Y/30 =', Y / 30, '→', [k for k, v in opts.items() if v == Y / 30])
