"""Q54 (真假推理): four projects 养老Y, 少儿托管S, 健身指导J, 图书角T; exactly one of the
four predictions is true. Enumerate all 16 opening plans."""
from itertools import product

imp = lambda a, b: (not a) or b
sols = []
for Y, S, J, T in product([False, True], repeat=4):
    preds = {
        '甲 S->T': imp(S, T),
        '乙 J->Y': imp(J, Y),
        '丙 Y,S,T至多一个': (Y + S + T) <= 1,
        '丁 S且非T': S and not T,
    }
    if sum(preds.values()) == 1:
        sols.append(dict(Y=Y, S=S, J=J, T=T, true=[k for k, v in preds.items() if v]))
for s in sols:
    print(s)
opts = {
    'A 开设图书角，不开设少儿托管': lambda s: s['T'] and not s['S'],
    'B 开设养老服务，不开设健身指导': lambda s: s['Y'] and not s['J'],
    'C 少儿托管和健身指导都开设': lambda s: s['S'] and s['J'],
    'D 养老服务和图书角都不开设': lambda s: not s['Y'] and not s['T'],
}
for k, f in opts.items():
    print(k, '-> must be true' if all(f(s) for s in sols) else '-> not necessarily')
