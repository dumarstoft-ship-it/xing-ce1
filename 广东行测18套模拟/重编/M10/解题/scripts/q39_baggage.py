"""M10 第39题：托运费10kg以内6元/kg，超出部分单价r(<6)。甲109.5元、乙78元，甲比乙重50%，求6−r。
选项 A1.5 B2.5 C3.5 D4.5"""
from fractions import Fraction as F
opts = {'A': F(3, 2), 'B': F(5, 2), 'C': F(7, 2), 'D': F(9, 2)}
fee = lambda w, r: 6 * w if w <= 10 else 60 + r * (w - 10)
# 乙：60+r(y−10)=78；甲：60+r(1.5y−10)=109.5 → 相减 0.5ry=31.5 → ry=63 → 63−10r=18 → r=4.5
r = (F(63) - 18) / 10
y = F(63) / r
print('r =', r, '乙重', y, 'kg，甲重', F(3, 2) * y, 'kg')
assert fee(y, r) == 78 and fee(F(3, 2) * y, r) == F(219, 2)
# 逐项代入：r = 6 − 选项，看能否同时满足两人
for k, dlt in opts.items():
    rr = 6 - dlt
    yy = 10 + F(18) / rr              # 由乙的费用定乙的重量
    print(k, '超出单价', rr, '乙重', yy, '甲费用', fee(F(3, 2) * yy, rr))
ok = [k for k, dlt in opts.items() if fee(F(3, 2) * (10 + F(18) / (6 - dlt)), 6 - dlt) == F(219, 2)]
assert ok == ['A']
print('答案：', ok, '；r=4.5本身是D项')
