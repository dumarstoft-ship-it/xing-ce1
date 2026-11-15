"""Q49 rule check on the fitted reconstructions (q49_fit_results.json from q49_fit_all.py).
Reports, for every stem figure and option: footprint (top view) vs the common stem footprint, max height, cube count,
surface area, front view and standard left view (back drawn on the left), then evaluates candidate rules:
  R1 'same top view as all stems'             R2 'max height 2 (like all stems)'
  R3 'row-wise: fig1 front view == fig3 left view' (only relation holding in rows 1-2 found by brute force)
  R4 'cube count constant in each row'        R5 'surface area constant in each row'
Also shows how A and C relate to stem figures (distractor construction)."""
import json
import os
D=os.path.dirname(os.path.abspath(__file__))+'/'
R=json.load(open(D+'q49_fit_results.json'))
names=['r1c1','r1c2','r1c3','r2c1','r2c2','r2c3','r3c1','r3c2','A','B','C','D']
S={n:frozenset(tuple(c) for c in R[n]['cubes']) for n in names}
def hm(s):
    h={}
    for x,d,z in s: h[(x,d)]=max(h.get((x,d),0),z+1)
    return h
def front(s): h=hm(s); return tuple(max([v for (x,d),v in h.items() if x==i] or [0]) for i in range(3))
def left(s):  h=hm(s); return tuple(max([v for (x,d),v in h.items() if d==j] or [0]) for j in (2,1,0))  # back..front
def surf(s): return sum(1 for (x,d,z) in s for dd in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)) if (x+dd[0],d+dd[1],z+dd[2]) not in s)
foot=lambda s: frozenset(hm(s))
stems=names[:8]
F0=foot(S['r1c1']); assert all(foot(S[n])==F0 for n in stems)
print('common stem footprint (x,d):',sorted(F0))
print(f"{'fig':5s} {'same_top':8s} {'maxH':4s} {'cubes':5s} {'surf':4s} front    left(back->front)")
for n in names:
    s=S[n]; print(f"{n:5s} {str(foot(s)==F0):8s} {max(hm(s).values()):<4d} {len(s):<5d} {surf(s):<4d} {front(s)} {left(s)}")
print('\nR1 same top view      ->',[o for o in 'ABCD' if foot(S[o])==F0])
print('R2 max height 2       ->',[o for o in 'ABCD' if max(hm(S[o]).values())==2])
print('R1 and R2             ->',[o for o in 'ABCD' if foot(S[o])==F0 and max(hm(S[o]).values())==2])
ok3=all(front(S[f'r{r}c1'])==left(S[f'r{r}c3']) for r in (1,2))
print('R3 fig1.front==fig3.left holds in rows 1,2:',ok3,' -> row 3 options:',[o for o in 'ABCD' if left(S[o])==front(S['r3c1'])])
for lab,fn in (('R4 cubes',len),('R5 surface',surf)):
    print(lab,'by row:',[[fn(S[f'r{r}c{c}']) for c in (1,2,3) if (r,c)!=(3,3)] for r in (1,2,3)],' options:',{o:fn(S[o]) for o in 'ABCD'})
print('\nDistractor construction:')
for o in 'ABCD':
    for n in stems:
        if S[n]<S[o] and len(S[o]-S[n])==1: print(f'  {o} = {n} + {sorted(S[o]-S[n])}  (same front/left view as {n}: {front(S[o])==front(S[n]) and left(S[o])==left(S[n])})')
