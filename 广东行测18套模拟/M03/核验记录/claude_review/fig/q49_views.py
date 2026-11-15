"""Q49: orthographic views (front/back/left/right/top) of each reconstructed solid as cropped binary images;
brute-force search for view-equality relations holding in rows 1 and 2, then test options for row 3."""
import json, itertools
import os
D=os.path.dirname(os.path.abspath(__file__))+'/'
R=json.load(open(D+'q49_fit_results.json'))
names=['r1c1','r1c2','r1c3','r2c1','r2c2','r2c3','r3c1','r3c2','A','B','C','D']
def crop(cells):
    if not cells: return frozenset()
    mc=min(c for c,r in cells); mr=min(r for c,r in cells)
    return frozenset((c-mc,r-mr) for c,r in cells)
def views(cs):
    X=max(x for x,d,z in cs); Dm=max(d for x,d,z in cs)
    v={}
    v['front']=crop({(x,z) for x,d,z in cs})
    v['back']=crop({(X-x,z) for x,d,z in cs})
    v['left']=crop({(Dm-d,z) for x,d,z in cs})      # back on the left, front on the right
    v['right']=crop({(d,z) for x,d,z in cs})
    v['top']=crop({(x,-d) for x,d,z in cs})
    return v
def show(s):
    if not s: return '-'
    W=max(c for c,r in s)+1; H=max(r for c,r in s)+1
    return '|'.join(''.join('#' if (c,r) in s else '.' for c in range(W)) for r in reversed(range(H)))
V={n:views([tuple(c) for c in R[n]['cubes']]) for n in names}
for n in names:
    print(n, {k:show(v) for k,v in V[n].items()})
# relations: within a row, view a of figure i == view b of figure j
rows=[['r1c1','r1c2','r1c3'],['r2c1','r2c2','r2c3']]
kinds=['front','back','left','right','top']
print('\nRelations holding in BOTH row 1 and row 2 (excluding top==top, which holds for every stem):')
rels=[]
for i,j in itertools.permutations(range(3),2):
    for ka in kinds:
        for kb in kinds:
            if all(V[r[i]][ka]==V[r[j]][kb] for r in rows):
                rels.append((i,ka,j,kb))
for rel in rels:
    i,ka,j,kb=rel
    if ka=='top' and kb=='top': continue
    if 2 not in (i,j): 
        ok=V['r3c%d'%(i+1)][ka]==V['r3c%d'%(j+1)][kb]
        print(f'  fig{i+1}.{ka} == fig{j+1}.{kb}   (row3 check: {ok})')
    else:
        k = i if j==2 else j
        kk, ko = (ka,kb) if j==2 else (kb,ka)
        good=[o for o in 'ABCD' if V['r3c%d'%(k+1)][kk]==V[o][ko]]
        print(f'  fig{i+1}.{ka} == fig{j+1}.{kb}   -> options satisfying for row3: {good}')

print('\nSet-operation relations view_c(fig3) == op(view_a(fig1), view_b(fig2)) holding in rows 1 and 2:')
ops={'union':lambda p,q:p|q,'inter':lambda p,q:p&q,'xor':lambda p,q:p^q}
def raw(cs,kind):
    X=max(x for x,d,z in cs); Dm=max(d for x,d,z in cs)
    return {'front':{(x,z) for x,d,z in cs},'left':{(2-d,z) for x,d,z in cs},'right':{(d,z) for x,d,z in cs},
            'back':{(2-x,z) for x,d,z in cs},'top':{(x,-d) for x,d,z in cs}}[kind]
C={n:[tuple(c) for c in R[n]['cubes']] for n in names}
for ka in kinds:
    for kb in kinds:
        for kc in kinds:
            for on,op in ops.items():
                if all(crop(op(raw(C[r[0]],ka),raw(C[r[1]],kb)))==V[r[2]][kc] for r in rows):
                    good=[o for o in 'ABCD' if crop(op(raw(C['r3c1'],ka),raw(C['r3c2'],kb)))==V[o][kc]]
                    print(f'  fig3.{kc} == {on}(fig1.{ka}, fig2.{kb}) -> row3 options: {good}')
# numeric features by row
print('\nNumeric features (front-view squares, left-view squares, top-view squares, cubes):')
for n in names:
    v=V[n]; print(n, len(v['front']), len(v['left']), len(v['top']), len(C[n]))

print('\nColumn-wise relations (holding in columns 1 and 2) between rows i,j; applied to column 3:')
cols=[['r1c1','r2c1','r3c1'],['r1c2','r2c2','r3c2']]
for i,j in itertools.permutations(range(3),2):
    for ka in kinds:
        for kb in kinds:
            if ka=='top' and kb=='top': continue
            if all(V[c[i]][ka]==V[c[j]][kb] for c in cols):
                col3=['r1c3','r2c3',None]
                if 2 in (i,j):
                    k=i if j==2 else j; kk,ko=(ka,kb) if j==2 else (kb,ka)
                    good=[o for o in 'ABCD' if V[col3[k]][kk]==V[o][ko]]
                    print(f'  row{i+1}.{ka} == row{j+1}.{kb} -> col3 options {good}')
                else:
                    print(f'  row{i+1}.{ka} == row{j+1}.{kb} (col3 check {V[col3[i]][ka]==V[col3[j]][kb]})')
# sequence (reading order 1..9) relations: fig n+? 
print('\nAll-view multiset per figure (front,left) as strings:')
for n in names: print(n, show(V[n]['front']), show(V[n]['left']))

print('\nSequence relations fig_n.ka == fig_{n+1}.kb over reading order (count of the 7 consecutive pairs that hold):')
seq=['r1c1','r1c2','r1c3','r2c1','r2c2','r2c3','r3c1','r3c2']
for ka in kinds:
    for kb in kinds:
        if ka=='top' and kb=='top': continue
        hold=[V[seq[i]][ka]==V[seq[i+1]][kb] for i in range(7)]
        if sum(hold)>=4: print(f'  {ka}->{kb}: {hold}  -> options with fig8.{ka}==opt.{kb}: {[o for o in "ABCD" if V["r3c2"][ka]==V[o][kb]]}')
