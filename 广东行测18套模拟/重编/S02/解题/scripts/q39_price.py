"""S02 第39题：降价20%后恢复原价，应上调多少。 选项 A10% B15% C20% D25%"""
from fractions import Fraction as F
p = F(100)
low = p * F(4, 5)
up = (p - low) / low
print('上调', up, '=', float(up) * 100, '%')
assert up == F(1, 4)
print('若按原价作基准算回20%（C）：', low * F(6, 5), '≠100')
