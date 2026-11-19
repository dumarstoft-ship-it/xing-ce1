"""M09 第66题：甲酸制氢微观示意图。反应前：1个HCOOH分子（1C、2O、2H）；反应后：1个H2分子、1个CO2分子。
核验：原子守恒、分子数变化、反应类型（一种物质生成两种物质→分解反应）。"""
from collections import Counter
before = [Counter({'C': 1, 'O': 2, 'H': 2})]                  # HCOOH
after = [Counter({'H': 2}), Counter({'C': 1, 'O': 2})]        # H2 + CO2
atoms_b = sum(before, Counter()); atoms_a = sum(after, Counter())
print('反应前原子', dict(atoms_b), '反应后原子', dict(atoms_a))
assert atoms_b == atoms_a                    # 原子守恒，图示已配平
print('分子个数：反应前', len(before), '→ 反应后', len(after))
assert len(after) > len(before)              # A 正确
print('反应物种类', len(before), '生成物种类', len(after), '→ 一变多，分解反应（B 化合反应错误）')
# C：H2是单质，CO2虽含碳但属无机物；D：任何化学反应都遵守能量守恒
