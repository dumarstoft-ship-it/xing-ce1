"""Q48: derive each row's identity pattern objectively from pixel correlation (original figure).
Two symbols are 'the same drawing' if their correlation as drawn >= 0.85 (observed same-symbol pairs
0.875-0.998; different-symbol pairs <= 0.76 except 180-degree twins which only match after rotation).
Then compare row patterns under three classification schemes:
  fine   : every distinct drawing is a distinct symbol
  coarse : a drawing and its 180-degree rotation count as the same symbol (axis orientation only)
  mixed  : the editor's implied scheme: upright/on-edge discs distinguished by visible end,
           tilted discs only by tilt direction."""
import numpy as np
exec(open('q48_symbols.py').read().split("names = list(symbols)")[0])   # reuse segmentation + score()
names = list(symbols)
rows = ['stem','A','B','C','D']
def same(p,q,rot=False):
    Q = np.rot90(symbols[q],2) if rot else symbols[q]
    return score(symbols[p],Q) >= 0.85
# fine classes by greedy clustering
cls = {}; reps = []
for nm in names:
    for i,r in enumerate(reps):
        if same(nm,r): cls[nm]=i; break
    else:
        reps.append(nm); cls[nm]=len(reps)-1
print('number of distinct drawings (fine classes):', len(reps), 'representatives:', reps)
# 180-degree twins among the classes
twin = {}
for i,r in enumerate(reps):
    for j,s in enumerate(reps):
        if i<j and same(r,s,rot=True): twin[i]=j; twin[j]=i
print('180-degree twin classes:', {reps[i]:reps[j] for i,j in twin.items() if i<j})
hand = {'stem':['U','D','D','R','LL','U','R','UL'],'A':['LL','L','L','UL','U','LL','UL','U'],
        'B':['R','U','U','LL','UR','R','LL','LR'],'C':['U','LL','UR','R','LR','U','R','D'],
        'D':['UR','LL','LL','LR','L','LL','LR','R']}
# consistency of the hand reading with the objective classes
lab_of_class = {}
ok=True
for r in rows:
    for i in range(8):
        c=cls[f'{r}{i+1}']; h=hand[r][i]
        if lab_of_class.setdefault(c,h)!=h: ok=False; print('MISMATCH',r,i+1,h,lab_of_class[c])
print('hand reading consistent with pixel classes:', ok, lab_of_class)
def canon(seq):
    m={}; return ''.join(m.setdefault(s,'abcdefgh'[len(m)]) for s in seq)
schemes = {
 'fine':   lambda h: h,
 'coarse': lambda h: {'U':'H','D':'H','R':'V','L':'V','LL':'\\','UR':'\\','UL':'/','LR':'/'}[h],
 'mixed':  lambda h: {'U':'U','D':'D','R':'R','L':'L','LL':'\\','UR':'\\','UL':'/','LR':'/'}[h],
}
for sname,f in schemes.items():
    st = canon([f(h) for h in hand['stem']])
    res = {o: canon([f(h) for h in hand[o]]) for o in 'ABCD'}
    agree = {o: sum(1 for i in range(8) for j in range(i+1,8) if (st[i]==st[j])==(res[o][i]==res[o][j])) for o in 'ABCD'}
    print(f'{sname:6s} stem={st}  ' + '  '.join(f'{o}={res[o]}{"*" if res[o]==st else ""}(pairs agreeing {agree[o]}/28)' for o in 'ABCD'))
