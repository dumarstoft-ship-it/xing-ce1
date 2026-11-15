"""Verify Q46: (1) my visual reading of the redrawn and original grids,
(2) the toroidal shift rule (up 1, left 1, wrap-around), (3) which option fits.
Visual reading entered by hand below (rows 1..9 top->bottom, cols 1..9 left->right)."""
from PIL import Image
import numpy as np

visual = {
 'P1': {1:[5,6],2:[5,7],3:[4,6],4:[4,7],5:[3,6],6:[5,7],7:[4,8]},
 'P2': {1:[4,6],2:[3,5],3:[3,6],4:[2,5],5:[4,6],6:[3,7],9:[4,5]},
 'P3': {1:[2,4],2:[2,5],3:[1,4],4:[3,5],5:[2,6],8:[3,4],9:[3,5]},
 'P4': {1:[1,4],2:[3,9],3:[2,4],4:[1,5],7:[2,3],8:[2,4],9:[1,3]},
 'P5': {1:[2,8],2:[1,3],3:[4,9],6:[1,2],7:[1,3],8:[2,9],9:[3,9]},
 'A':  {1:[2,9],2:[3,8],5:[1,9],6:[2,9],7:[1,8],8:[1,9],9:[1,7]},
 'B':  {1:[2,9],2:[3,8],5:[1,9],6:[2,9],7:[1,8],8:[2,8],9:[1,7]},
 'C':  {1:[2,9],2:[3,9],5:[1,9],6:[2,9],7:[1,8],8:[2,7],9:[1,7]},
 'D':  {1:[2,9],2:[3,8],5:[1,8],6:[2,8],7:[1,7],8:[2,8],9:[1,7]},
}
def to_mat(d):
    m=np.zeros((9,9),int)
    for r,cs in d.items():
        for c in cs: m[r-1,c-1]=1
    return m
V={k:to_mat(v) for k,v in visual.items()}

def sample(path, origins, cell, thr=110):
    """origins: dict name->(x0,y0) of the grid's top-left inner corner; cell: cell size (px).
    Returns 9x9 matrix: 1 if the central 40% of the cell is mostly dark."""
    a=np.array(Image.open(path).convert('L')).astype(float)
    out={}
    for k,(x0,y0) in origins.items():
        m=np.zeros((9,9),int)
        for r in range(9):
            for c in range(9):
                cx=x0+(c+0.5)*cell; cy=y0+(r+0.5)*cell
                h=cell*0.2
                patch=a[int(cy-h):int(cy+h)+1, int(cx-h):int(cx+h)+1]
                m[r,c]=1 if patch.mean()<thr else 0
        out[k]=m
    return out

# Redrawn: grid lines at x0=65 (+582 per panel), cell 48; rows: top grid starts y=66, bottom y=840
red = '/home/user/xing-ce1/广东行测18套模拟/M04/assets/q46_pixel_shift.png'
ro={}
for i,k in enumerate(['P1','P2','P3','P4','P5']): ro[k]=(65+582*i, 66)
for i,k in enumerate(['A','B','C','D']): ro[k]=(644+582*i, 840)
R=sample(red, ro, 48.1)

# Original: panel grid x starts 13 (+~97.3 per panel) ; y starts 14.5 ; cell ~9.72
org = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s21_p11_i00.png'
oo={}
for i,(k,x) in enumerate(zip(['P1','P2','P3','P4','P5'],[13,110.5,208,305,403])): oo[k]=(x,14.5)
for i,(k,x) in enumerate(zip(['A','B','C','D'],[112,209.5,307,404.5])): oo[k]=(x,144.5)
O=sample(org, oo, 9.72)

ok=True
for k in V:
    same_r=(R[k]==V[k]).all(); same_o=(O[k]==V[k]).all()
    print(f'{k}: visual==redrawn {same_r}; visual==original {same_o}')
    if not same_r: print(' redrawn diff cells (r,c):', [(r+1,c+1) for r,c in zip(*np.where(R[k]!=V[k]))])
    if not same_o: print(' original diff cells (r,c):', [(r+1,c+1) for r,c in zip(*np.where(O[k]!=V[k]))])

def shift(m): return np.roll(np.roll(m,-1,axis=0),-1,axis=1)   # up 1, left 1, wrap
seq=['P1','P2','P3','P4','P5']
for a,b in zip(seq,seq[1:]):
    print(f'shift({a})=={b}:', (shift(V[a])==V[b]).all())
pred=shift(V['P5'])
for k in 'ABCD':
    diff=[(r+1,c+1) for r,c in zip(*np.where(pred!=V[k]))]
    print(f'option {k}: matches prediction={len(diff)==0}; differing cells={diff}')
# Check alternative "uniform" shifts that map P1->P2 (to ensure uniqueness of the motion)
for dr in range(-4,5):
    for dc in range(-4,5):
        if all((np.roll(np.roll(V[a],dr,0),dc,1)==V[b]).all() for a,b in zip(seq,seq[1:])):
            print('consistent torus shift (dr,dc)=',dr,dc)
