# 第35题：圆形数阵（左上a、右上b、左下c、右下d），枚举简单等式，在三个已知圆上都成立者求第4圆的“？”
from itertools import permutations, product
from fractions import Fraction as F

circles = [(2, 6, 10, 8), (5, 11, 4, 3), (7, 17, 11, 4)]
last = (None, 9, 18, 3)          # ？在左上
names = 'abcd'
ops = {'+': lambda x, y: x + y, '-': lambda x, y: x - y, '*': lambda x, y: x * y,
       '/': lambda x, y: (F(x) / y) if y != 0 else None}

def ev(expr_vals, op_list):
    v = F(expr_vals[0])
    for o, x in zip(op_list, expr_vals[1:]):
        if v is None: return None
        v = ops[o](v, x)
    return v

found = {}
# 形式1：x op y = z op w（四个位置各用一次）
for p in permutations(range(4)):
    for o1, o2 in product(ops, repeat=2):
        def holds(c):
            l = ops[o1](F(c[p[0]]), c[p[1]]); r = ops[o2](F(c[p[2]]), c[p[3]])
            return l is not None and r is not None and l == r
        if all(holds(c) for c in circles):
            sols = [q for q in range(-50, 200) if holds((q,) + last[1:])]
            key = f'{names[p[0]]}{o1}{names[p[1]]} = {names[p[2]]}{o2}{names[p[3]]}'
            found[key] = sols
# 形式2：(x op y) op z = w
for p in permutations(range(4)):
    for o1, o2 in product(ops, repeat=2):
        def holds(c):
            l = ops[o1](F(c[p[0]]), c[p[1]])
            if l is None: return False
            l = ops[o2](l, c[p[2]])
            return l is not None and l == c[p[3]]
        if all(holds(c) for c in circles):
            sols = [q for q in range(-50, 200) if holds((q,) + last[1:])]
            key = f'({names[p[0]]}{o1}{names[p[1]]}){o2}{names[p[2]]} = {names[p[3]]}'
            found[key] = sols
# 形式3：四数和/积为常数，或 x op y op z op w 为常数
for o in product(ops, repeat=3):
    for p in permutations(range(4)):
        vals = [ev([c[i] for i in p], o) for c in circles]
        if None not in vals and len(set(vals)) == 1:
            sols = [q for q in range(-50, 200) if ev([((q,) + last[1:])[i] for i in p], o) == vals[0]]
            found[f'{names[p[0]]}{o[0]}{names[p[1]]}{o[1]}{names[p[2]]}{o[2]}{names[p[3]]} = {vals[0]}（从左到右算）'] = sols
print('a=左上，b=右上，c=左下，d=右下；三个已知圆都成立的等式及其给出的“？”：')
for k, v in found.items():
    print(' ', k, '→ ？=', v)
print('各选项是否被某条等式给出：', {opt: any(opt in v for v in found.values()) for opt in (9, 8, 7, 6)})
