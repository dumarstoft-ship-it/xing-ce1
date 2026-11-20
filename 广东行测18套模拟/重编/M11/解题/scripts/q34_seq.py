"""M11 第34题：1/2，2/6，2/8，3/15，（ ）  选项 A3/18 B3/16 C5/25 D7/25（原卷公式图，已核对）
约分后为1/2、1/3、1/4、1/5 → 1/6；也可看分母÷分子=2、3、4、5 → 6。"""
from fractions import Fraction as F
raw = [(1, 2), (2, 6), (2, 8), (3, 15)]
opts = {'A': (3, 18), 'B': (3, 16), 'C': (5, 25), 'D': (7, 25)}
assert [F(a, b) for a, b in raw] == [F(1, n) for n in range(2, 6)]
ok = [k for k, (a, b) in opts.items() if F(a, b) == F(1, 6)]
print('等于1/6的选项：', ok, '；各选项的值', {k: str(F(a, b)) for k, (a, b) in opts.items()})
assert ok == ['A']
assert [b / a for a, b in raw] == [2, 3, 4, 5]
# C项5/25=1/5与第4项相等，只是“1/5”的另一种写法
