from itertools import product
D = ['人事','科研','教育','财务','宣传','后勤','工会']
P = ['王','卫','丁']
def solve(exact):
    sols = []
    for a in product(P, repeat=7):
        s = dict(zip(D, a))
        if s['教育'] != s['财务']: continue
        if s['宣传'] != s['后勤']: continue
        cnt = {x: a.count(x) for x in P}
        if not cnt['丁'] > cnt['卫']: continue
        c4 = [s['教育']=='王', s['工会']=='王']
        c5 = [s['工会']=='卫', s['后勤']=='卫']
        if exact:
            if sum(c4)!=1 or sum(c5)!=1: continue
        else:
            if sum(c4)<1 or sum(c5)<1: continue
        sols.append(s)
    return sols
opts = {
 'A': lambda s: s['人事']=='王' and s['宣传']=='王',
 'B': lambda s: s['人事']=='丁' and s['宣传']=='丁',
 'C': lambda s: s['科研']=='丁' and s['宣传']=='丁',
 'D': lambda s: s['教育']=='王' and s['宣传']=='王',
}
for exact in (True, False):
    sols = solve(exact)
    print('exact' if exact else 'at-least', 'solutions:', len(sols))
    for k,f in opts.items():
        n = sum(f(s) for s in sols)
        print('  ', k, 'possible' if n else 'IMPOSSIBLE', n)
    if exact:
        for s in sols: print('   ', ' '.join(f'{d}{s[d]}' for d in D))
