"""Q60 真假推理：穷举4人帽子颜色（红=说真话，蓝=说假话），检验小强帽色。"""
from itertools import product

names = ['小红', '小明', '小丽', '小强']
sols = []
for cols in product('RB', repeat=4):
    h = dict(zip(names, cols))
    others = lambda me: [h[n] for n in names if n != me]
    s_hong = sorted(others('小红')) == sorted(['R', 'R', 'B'])     # 看到2红1蓝
    s_ming = others('小明').count('B') == 3                          # 看到3蓝
    s_li = others('小丽').count('R') == 3                            # 看到3红
    stmts = {'小红': s_hong, '小明': s_ming, '小丽': s_li}
    if all((h[n] == 'R') == v for n, v in stmts.items()):
        sols.append(h)
print('一致的情形:')
for s in sols:
    print('  ', s)
qiang = {s['小强'] for s in sols}
print('小强可能的颜色:', qiang)
print('A 可能红也可能蓝:', qiang == {'R', 'B'})
print('B 一定红:', qiang == {'R'})
print('C 与小明相同:', all(s['小强'] == s['小明'] for s in sols))
print('D 一定蓝:', qiang == {'B'})
