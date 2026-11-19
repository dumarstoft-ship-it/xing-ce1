"""S01 第70题：A项“通过光合作用，绿叶只能生成碳水化合物”——核对光合作用总反应式的原子守恒：
6CO2 + 6H2O →(光、叶绿体) C6H12O6 + 6O2，产物除葡萄糖（碳水化合物）外还有氧气。"""
from collections import Counter
def atoms(formula_counts):
    c = Counter()
    for k, n in formula_counts:
        for el, m in k.items():
            c[el] += m * n
    return c
CO2, H2O, GLU, O2 = {'C': 1, 'O': 2}, {'H': 2, 'O': 1}, {'C': 6, 'H': 12, 'O': 6}, {'O': 2}
left = atoms([(CO2, 6), (H2O, 6)])
right = atoms([(GLU, 1), (O2, 6)])
print('反应物', dict(left), '生成物', dict(right))
assert left == right
print('生成物有C6H12O6和O2两种；且叶片还能以光合产物为原料合成蛋白质、脂肪等，“只能生成碳水化合物”不准确，A为所选。')
