from itertools import product, combinations
G = ['台球', '乒乓球', '羽毛球', '登山']
P = '甲乙丙丁戊己庚'
pairs = [frozenset(c) for c in combinations(G, 2)]
M = []
for ch in product(pairs, repeat=7):
    A = dict(zip(P, ch))
    if A['丁'] != A['戊'] or A['己'] != A['庚']: continue
    if '台球' in A['甲'] and '台球' not in A['丁']: continue
    if {p for p in P if '乒乓球' in A[p]} != {'乙', '丙'}: continue
    sizes = {g: sum(g in A[p] for p in P) for g in G}
    if any(not 2 <= sizes[g] <= 5 for g in G): continue
    M.append(A)
print('base models', len(M))
M99 = [A for A in M if {p for p in P if '登山' in A[p]} == {'己', '庚'}]
opts99 = {'A': lambda A: A['甲'] == {'台球', '羽毛球'}, 'B': lambda A: A['乙'] == {'台球', '羽毛球'},
          'C': lambda A: A['己'] == {'台球', '登山'}, 'D': lambda A: A['庚'] == {'羽毛球', '登山'}}
print('99 models', len(M99), {k: (all(f(A) for A in M99), any(f(A) for A in M99)) for k, f in opts99.items()})
M100 = [A for A in M if '台球' not in A['乙'] and '台球' not in A['丁']]
imp = lambda a, b: (not a) or b
opts100 = {'A': lambda A: imp('台球' in A['己'], '登山' in A['丙']), 'B': lambda A: imp('台球' in A['庚'], '台球' in A['戊']),
           'C': lambda A: imp('羽毛球' in A['甲'], '登山' in A['庚']), 'D': lambda A: imp('羽毛球' in A['乙'], '登山' in A['己'])}
print('100 models', len(M100), {k: all(f(A) for A in M100) for k, f in opts100.items()})
# premise non-vacuous for each conditional option
print({k: any(('台球' in A['己']) if k=='A' else ('台球' in A['庚']) if k=='B' else ('羽毛球' in A['甲']) if k=='C' else ('羽毛球' in A['乙']) for A in M100) for k in 'ABCD'})
