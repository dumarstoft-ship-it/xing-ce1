"""第47题：九宫格各图都画在3x3格点(0..2)上（图像坐标，y向下）。
把每条线拆成格点间的单位段，验证“第一图与第二图去同存异，再整体变换=第三图”，
对8种对称变换逐一检验，找出第1、2行都成立的变换，再套用到第3行，与四个选项比对。"""
from itertools import product

def unit_segments(p, q):
    (x0, y0), (x1, y1) = p, q
    dx, dy = x1 - x0, y1 - y0
    from math import gcd
    g = gcd(abs(dx), abs(dy))
    sx, sy = dx // g, dy // g
    segs = set()
    for i in range(g):
        a = (x0 + i * sx, y0 + i * sy)
        b = (x0 + (i + 1) * sx, y0 + (i + 1) * sy)
        segs.add(tuple(sorted([a, b])))
    return segs

def fig(*lines):
    s = set()
    for p, q in lines:
        s |= unit_segments(p, q)
    return frozenset(s)

F = {
 '11': fig(((0,0),(2,0)), ((2,0),(0,1)), ((0,1),(2,2)), ((0,2),(2,2)), ((0,1),(0,2))),
 '12': fig(((0,0),(0,1)), ((0,1),(2,0)), ((0,2),(2,1)), ((2,1),(2,2)), ((0,2),(2,2))),
 '13': fig(((0,0),(2,0)), ((2,0),(2,2)), ((0,0),(1,2)), ((1,0),(0,2)), ((0,2),(1,2))),
 '21': fig(((0,0),(0,1)), ((0,1),(2,1)), ((1,0),(1,2)), ((1,0),(0,2)), ((0,2),(2,2))),
 '22': fig(((0,0),(2,0)), ((0,0),(0,1)), ((1,0),(1,2)), ((2,0),(2,2)), ((0,2),(2,2)), ((1,1),(2,2))),
 '23': fig(((0,0),(2,1)), ((1,0),(1,2)), ((2,0),(2,2)), ((0,2),(2,2)), ((0,2),(1,1))),
 '31': fig(((0,0),(1,0)), ((0,0),(0,1)), ((0,1),(1,1)), ((1,0),(1,2)), ((1,2),(2,2)), ((2,1),(2,2)), ((0,2),(2,1)), ((1,1),(2,0))),
 '32': fig(((0,0),(0,1)), ((0,1),(1,1)), ((0,0),(2,1)), ((2,1),(0,2)), ((2,1),(2,2)), ((1,2),(2,2))),
}
OPT = {
 'A': fig(((0,0),(0,1)), ((0,1),(2,1)), ((2,0),(2,1)), ((2,0),(1,2)), ((1,1),(2,2))),
 'B': fig(((0,0),(1,0)), ((1,0),(1,2)), ((1,2),(2,2)), ((0,0),(2,1)), ((1,1),(2,0))),
 'C': fig(((0,0),(1,0)), ((1,0),(1,2)), ((0,0),(2,1)), ((1,1),(2,0))),
 'D': fig(((0,1),(2,1)), ((2,0),(2,1)), ((2,0),(1,2)), ((1,1),(2,2))),
}
# 8 symmetries of the square on 0..2 grid, image coords (y down)
T = {
 'id':      lambda x, y: (x, y),
 'rot90cw': lambda x, y: (2 - y, x),
 'rot180':  lambda x, y: (2 - x, 2 - y),
 'rot90ccw':lambda x, y: (y, 2 - x),
 'flipH':   lambda x, y: (2 - x, y),
 'flipV':   lambda x, y: (x, 2 - y),
 'transp':  lambda x, y: (y, x),
 'antitr':  lambda x, y: (2 - y, 2 - x),
}
def apply(t, s):
    return frozenset(tuple(sorted([t(*a), t(*b)])) for a, b in s)

for row in '123':
    x = F[row + '1'] ^ F[row + '2']
    union = F[row + '1'] | F[row + '2']
    inter = F[row + '1'] & F[row + '2']
    if row != '3':
        hits = [n for n, t in T.items() if apply(t, x) == F[row + '3']]
        hu = [n for n, t in T.items() if apply(t, union) == F[row + '3']]
        hi = [n for n, t in T.items() if apply(t, inter) == F[row + '3']]
        print(f'row{row}: XOR->third via {hits}; union via {hu}; intersection via {hi}')
    else:
        for n, t in T.items():
            m = [k for k, v in OPT.items() if apply(t, x) == v]
            if m:
                print(f'row3: XOR transformed by {n} equals option {m}')
