"""M10 第36题：液体占桶容量40%，再加16升后液体体积为原来的1.5倍，求桶容量。 选项 A20 B40 C60 D80"""
from fractions import Fraction as F
opts = {'A': 20, 'B': 40, 'C': 60, 'D': 80}
# 增加的16升 = 原液体的0.5倍 → 原液体32升 → 容量 32÷40% = 80
orig = F(16) / (F(3, 2) - 1)
cap = orig / F(2, 5)
print('原液体', orig, '升，容量', cap, '升')
# 逐项代入验证
for k, c in opts.items():
    v0 = F(2, 5) * c
    print(k, c, '原液体', float(v0), '加16升后为原来的', float((v0 + 16) / v0), '倍')
ok = [k for k, c in opts.items() if (F(2, 5) * c + 16) == F(3, 2) * F(2, 5) * c]
assert ok == ['D'] and cap == 80
# 另一种看法：40%×1.5=60%，16升对应20%的容量
assert F(16) / (F(3, 5) - F(2, 5)) == 80
print('答案：', ok)
