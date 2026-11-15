"""Verify Q47: visual reading (hand-entered) vs pixel sampling of redrawn and original,
then the 'snake along a fixed route: tail +1, head +2 per step' rule."""
from PIL import Image
import numpy as np
visual = {  # (row,col) black cells, rows/cols 1..5
 'P1': [(1,1),(2,1),(3,1),(4,1),(5,1)],
 'P2': [(2,1),(3,1),(4,1),(5,1),(5,2),(5,3)],
 'P3': [(3,1),(4,1),(5,1),(5,2),(5,3),(4,3),(3,3)],
 'P4': [(4,1),(5,1),(5,2),(5,3),(4,3),(3,3),(2,3),(1,3)],
 'P5': [(5,1),(5,2),(5,3),(4,3),(3,3),(2,3),(1,3),(1,4),(1,5)],
 'A':  [(1,3),(2,3),(3,3),(4,3),(5,3),(1,4),(1,5),(2,5),(3,5),(4,5)],
 'B':  [(5,2),(5,3),(4,3),(3,3),(2,3),(1,3),(1,4),(1,5),(2,5),(3,5)],
 'C':  [(5,1),(5,2),(5,3),(4,3),(3,3),(2,3),(1,3),(1,4),(1,5),(2,5)],
 'D':  [(5,2),(5,3),(4,3),(3,3),(2,3),(1,3),(1,4),(1,5)],
}
def mat(cells):
    m=np.zeros((5,5),int)
    for r,c in cells: m[r-1,c-1]=1
    return m
V={k:mat(v) for k,v in visual.items()}
def sample(path, origins, cell, thr=110):
    a=np.array(Image.open(path).convert('L')).astype(float); out={}
    for k,(x0,y0) in origins.items():
        m=np.zeros((5,5),int)
        for r in range(5):
            for c in range(5):
                cx=x0+(c+0.5)*cell; cy=y0+(r+0.5)*cell; h=cell*0.2
                m[r,c]=int(a[int(cy-h):int(cy+h)+1,int(cx-h):int(cx+h)+1].mean()<thr)
        out[k]=m
    return out
red='/home/user/xing-ce1/广东行测18套模拟/M04/assets/q47_growing_path.png'
ro={k:(65+582*i,66) for i,k in enumerate(['P1','P2','P3','P4','P5'])}
ro.update({k:(644+582*i,840) for i,k in enumerate('ABCD')})
R=sample(red,ro,84.2)
org='/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s25_p11_i00.png'
# original grid: panel1 inner grid x 14..92 (5 cells ~15.6px), y 17..93
oo={k:(x,17) for k,x in zip(['P1','P2','P3','P4','P5'],[14,112,210,308,405])}
oo.update({k:(x,147) for k,x in zip('ABCD',[114,212,310,408])})
O=sample(org,oo,15.6)
for k in V:
    print(k,'visual==redrawn',(R[k]==V[k]).all(),'visual==original',(O[k]==V[k]).all())
    for nm,M in (('red',R),('org',O)):
        if not (M[k]==V[k]).all(): print('  ',nm,'diff',[(r+1,c+1) for r,c in zip(*np.where(M[k]!=V[k]))]); print(M[k])
# Route: down col1, right row5 to col3, up col3, right row1 to col5, down col5
route=[(r,1) for r in range(1,6)]+[(5,2),(5,3)]+[(r,3) for r in range(4,0,-1)]+[(1,4),(1,5)]+[(r,5) for r in range(2,6)]
def seg(i,j): return mat(route[i:j+1])
for k,(i,j) in zip(['P1','P2','P3','P4','P5'],[(0,4),(1,6),(2,8),(3,10),(4,12)]):
    print(k,'== route[%d..%d]'%(i,j),(seg(i,j)==V[k]).all())
pred=seg(5,14)
for k in 'ABCD':
    idx=sorted(route.index(c) for c in visual[k]) if all(c in route for c in visual[k]) else None
    print('option',k,'cells',len(visual[k]),'route idx',idx,'== pred',(V[k]==pred).all())
