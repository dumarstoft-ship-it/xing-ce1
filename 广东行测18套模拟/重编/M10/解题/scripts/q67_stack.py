"""M10 第67题：甲叠放在乙上，乙受水平向右拉力F，甲、乙都静止。取一组数检验四个选项。
选项 A 甲乙之间至少2对相互作用力 B 乙对甲支持力>甲重力 C F向左则不再静止 D 地面对乙摩擦力等于F"""
g = 10.0
m_jia, m_yi, F = 2.0, 3.0, 10.0
mu_ground = 0.5                      # 地面最大静摩擦（近似取滑动摩擦）
f_max = mu_ground * (m_jia + m_yi) * g
# 甲：竖直方向 G甲 与 N(乙→甲) 平衡；水平方向不受其他力，故乙对甲的静摩擦为0
N_on_jia = m_jia * g
f_between = 0.0
# 整体：水平方向 F 与地面静摩擦平衡
f_ground = F
assert F <= f_max
pairs = {'压力—支持力': N_on_jia, '静摩擦力': f_between}
print('甲乙之间的相互作用力（不计万有引力）：', pairs, '→ 非零的只有', [k for k, v in pairs.items() if v], '一对')
print('乙对甲支持力', N_on_jia, '甲重力', m_jia * g, '相等')
for direction in (+1, -1):
    need = abs(direction * F)
    print('F方向', '向右' if direction > 0 else '向左', '需地面静摩擦', need, '≤最大静摩擦', f_max, '→ 静止' if need <= f_max else '→ 滑动')
print('地面对乙的摩擦力大小', f_ground, '= F', F)
truth = {'A': sum(1 for v in pairs.values() if v) >= 2, 'B': N_on_jia > m_jia * g,
         'C': F > f_max, 'D': f_ground == F}
print(truth)
assert [k for k, v in truth.items() if v] == ['D']
