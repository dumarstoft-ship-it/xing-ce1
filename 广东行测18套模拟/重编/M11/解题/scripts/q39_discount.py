"""M11 第39题：打九折利润减少一半；打八五折利润减少22.5元。求原价销售的利润。 选项 A15 B22.5 C30 D45"""
from fractions import Fraction as F
P = F(45, 2) / F(15, 100)        # 八五折比原价少收15%P，就是利润减少的22.5元 → 原价150
profit = 2 * (P / 10)            # 九折少收10%P=15元，是利润的一半
cost = P - profit
print('原价', P, '利润', profit, '成本', cost)
assert profit == 30
assert (P * F(9, 10) - cost) * 2 == profit and profit - (P * F(85, 100) - cost) == F(45, 2)
# 易错核对：把22.5当成利润的一半之类：22.5是原价的15%，原价的10%=15元才是利润的一半
print('原价的10% =', P / 10, '（A项15是“利润的一半”，不是利润）')
