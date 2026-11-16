# 第42题：小王三关 80%、60%、50%；小李 90%、50%、20%；两人均通过三关的概率。
from fractions import Fraction as F
wang = F(80, 100) * F(60, 100) * F(50, 100)
li = F(90, 100) * F(50, 100) * F(20, 100)
both = wang * li
print("小王全过", float(wang), "小李全过", float(li), "两人都全过", float(both))
assert both == F(216, 10000)
print("答案: A 2.16%（C=24%只算小王，B=9%只算小李，D=33%把两人相加）")
