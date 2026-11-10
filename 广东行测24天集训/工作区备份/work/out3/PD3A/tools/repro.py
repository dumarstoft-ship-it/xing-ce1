"""Re-run PD3A program checks from the source PDFs.  python3 repro.py [workdir]
  - GK2024F-80 / GK2025D-81: fold each option net onto a 3x2x2 box (unit squares), compare cube colours
  - GK2025D-78: read 19-cell brick patterns, compare adjacent figures row by row
  - GK2025D-83: read 5x5 ball grids, find mirror axes, count black balls on the axis
  - GK2023F-81: fold the 24-square net onto a 2x2x2 cube, read the arrow face (hand-coded net)
  - GDXD2019SW-80: strip folding as successive reflections (hand-coded crease directions)"""
import sys, os, subprocess, json, numpy as np
from PIL import Image
T=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,T)
W=sys.argv[1] if len(sys.argv)>1 else '/tmp/pd3a_repro'; os.makedirs(W,exist_ok=True)
def emb(tag,q):
    out=subprocess.run([sys.executable,f'{T}/emb.py',tag,str(q),f'{W}/emb_{tag}-{q}'],capture_output=True,text=True).stdout.split()
    return out[0]
from netparse import parse, parse2, show
from cuboidcheck import check
# GK2024F-80
a=np.asarray(Image.open(emb('GK2024F',80)).convert('L')).astype(int)
tg={(1,1,1),(0,0,1),(2,1,0),(2,0,0)}
for name,(x0,x1) in zip('ABCD',[(160,244),(266,369),(384,477),(495,589)]):
    cells,p=parse(a,x0,20,x1,110); print('GK2024F-80',name,'(foldings, uniform-colour, match)',check(cells,(3,2,2),tg))
# GK2025D-81
a=np.asarray(Image.open(emb('GK2025D',81)).convert('L')).astype(int)
tg={(1,1,1),(1,0,1),(1,1,0),(2,0,0)}
for name,(x0,x1) in zip('ABCD',[(0,133),(152,287),(305,440),(458,592)]):
    cells,g=parse2(a,x0,82,x1,170,12.6); cells={k:('G' if v=='B' else v) for k,v in cells.items()}
    print('GK2025D-81',name,'(foldings, uniform-colour, match)',check(cells,(3,2,2),tg))
# GK2025D-78
a=np.asarray(Image.open(emb('GK2025D',78)).convert('L')).astype(int)
figs={'f1':(17,22,84,89),'f2':(115,22,182,89),'f3':(217,23,283,90),'f4':(318,22,385,89),'f5':(415,22,482,89),
      'A':(120,153,187,220),'B':(219,153,285,220),'C':(315,153,382,220),'D':(413,154,480,220)}
ns=[3,4,5,4,3]
def read(b):
    x0,y0,x1,y1=b; xc=(x0+x1)/2; h=(y1-y0)/5; w=(x1-x0)/5; rows=[]
    for r,n in enumerate(ns):
        yc=y0+h*(r+0.5); rows.append(''.join('B' if a[int(yc)-2:int(yc)+3,int(xc+(j-(n-1)/2)*w)-2:int(xc+(j-(n-1)/2)*w)+3].mean()<120 else 'W' for j in range(n)))
    return rows
R={k:read(v) for k,v in figs.items()}
seq=['f1','f2','f3','f4','f5']
for p,q in zip(seq,seq[1:]): print('GK2025D-78',p,'->',q,'rows differ',[i for i in range(5) if R[p][i]!=R[q][i]])
for o in 'ABCD': print('GK2025D-78 f5 ->',o,'rows differ',[i for i in range(5) if R['f5'][i]!=R[o][i]])
# GK2023F-81
from boxfold import fold
def big(r,c): return {(r,c),(r,c+1),(r+1,c),(r+1,c+1)}
net=set()
for (r,c) in [(0,5),(2,1),(2,3),(2,5),(4,3)]: net|=big(r,c)
flaps={(0,7):(0,1),(2,7):(-1,0),(3,0):(0,-1),(6,4):(-1,0)}; net|=set(flaps)
fr=fold(net,(2,2,2))[0]; n=np.array(fr[(0,7)][1]); cen=np.array([1.,1,1])+n
tang=[np.array(t) for t in [(1,0,0),(0,1,0),(0,0,1),(-1,0,0),(0,-1,0),(0,0,-1)] if np.dot(t,n)==0]
pats=set()
for su in tang:
    sv=[t for t in tang if (np.cross(su,-t)==n).all()][0]; grid={}
    for f,(dr,dc) in flaps.items():
        c,nn,u,v=fr[f]; a3=dc*u+dr*v; rel=np.array(c)-cen
        grid[(0 if np.dot(rel,sv)<0 else 1, 0 if np.dot(rel,su)<0 else 1)]={(0,1):'→',(0,-1):'←',(-1,0):'↑',(1,0):'↓'}[(int(np.dot(a3,sv)),int(np.dot(a3,su)))]
    pats.add(grid[(0,0)]+grid[(0,1)]+'/'+grid[(1,0)]+grid[(1,1)])
print('GK2023F-81 arrow face (4 rotations):',pats,' options A →↓/↑←  B →↑/↑↓  C ↑←/↓↓  D →←/↑←')
# GDXD2019SW-80
from strip import turns
for k,v in {'A':'\\\\//','B':'\\//\\','C':'/\\/\\','D':'////'}.items(): print('GDXD2019SW-80',k,v,turns(list(v)),'(target LLRR or mirror RRLL)')
# GK2025D-83 (needs PD2A rq.py renderer)
sys.path.insert(0,'/home/user/work/out2/PD2A/tools')
from rq import render
img=render('GK2025D',83,f'{W}/GK2025D-83.png',250,keep_opts=True)
a=np.asarray(Image.open(img).convert('L')).astype(int)
xs=[(66,238),(262,436),(458,632),(651,825),(840,1013),(1033,1206)]; y0,y1=113,285
for i,(x0,x1) in enumerate(xs,1):
    pts={(r,c) for r in range(5) for c in range(5) if a[int(y0+(r+.5)*(y1-y0)/5)-3:int(y0+(r+.5)*(y1-y0)/5)+4,int(x0+(c+.5)*(x1-x0)/5)-3:int(x0+(c+.5)*(x1-x0)/5)+4].mean()<100}
    ax=[]
    for k in range(9):
        if {(r,k-c) for r,c in pts}==pts: ax.append(('V',k/2,sum(1 for r,c in pts if 2*c==k)))
        if {(k-r,c) for r,c in pts}==pts: ax.append(('H',k/2,sum(1 for r,c in pts if 2*r==k)))
        if {(k-c,k-r) for r,c in pts}==pts: ax.append(('anti',k,sum(1 for r,c in pts if r+c==k)))
    for k in range(-4,5):
        if {(c-k,r+k) for r,c in pts}==pts: ax.append(('diag',k,sum(1 for r,c in pts if c-r==k)))
    print('GK2025D-83 fig',i,'black',len(pts),'axes (type,pos,black-on-axis)',ax)
