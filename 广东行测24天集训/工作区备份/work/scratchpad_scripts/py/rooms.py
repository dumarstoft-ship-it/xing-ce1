from itertools import permutations
names = ['甲','乙','丙','丁','戊','己','庚','辛']
sols = []
for perm in permutations(range(1,9)):
    p = dict(zip(names, perm))
    if abs(p['甲']-p['丙']) != 4: continue
    if abs(p['乙']-p['己']) != 3: continue
    if p['庚']-p['丁'] != 3: continue
    if abs(p['辛']-p['戊']) != 2: continue
    sols.append(p)
print('base solutions:', len(sols))
def show(p):
    order = sorted(names, key=lambda n: p[n])
    return ''.join(order)

# Y15: 庚 and 辛 adjacent
y15 = [p for p in sols if abs(p['庚']-p['辛'])==1]
print('Y15 count', len(y15))
for p in y15: print('  ', show(p))
opts15 = {'A':lambda p:p['甲']==2,'B':lambda p:p['乙']==5,'C':lambda p:p['丁']==1,'D':lambda p:p['己']==4}
for k,f in opts15.items():
    print('Y15', k, 'possible' if any(f(p) for p in y15) else 'impossible', sum(f(p) for p in y15))

# Y16: 乙 and 戊 adjacent
y16 = [p for p in sols if abs(p['乙']-p['戊'])==1]
print('Y16 count', len(y16))
for p in y16: print('  ', show(p))
def between(p, x):
    lo, hi = sorted([p['甲'], p['丙']])
    return lo < p[x] < hi
for k,x in zip('ABCD',['丁','戊','庚','辛']):
    print('Y16', k, x, 'always' if all(between(p,x) for p in y16) else 'not always', sum(between(p,x) for p in y16))
