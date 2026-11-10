import numpy as np
from PIL import Image
from scipy import ndimage as nd
S='/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pd3a'
a=np.asarray(Image.open(f'{S}/h/emb_GK2025D-78_0.png').convert('L')).astype(int)
H,W=a.shape
dark=a<100
# find each figure blob (connected dark+gray area) per row band
def blobs(y0,y1):
    m=(a[y0:y1]<200)
    m=nd.binary_closing(m,iterations=2)
    lab,n=nd.label(m)
    out=[]
    for i in range(1,n+1):
        ys,xs=np.where(lab==i)
        if len(ys)<800: continue
        out.append((xs.min(),ys.min()+y0,xs.max(),ys.max()+y0))
    return sorted(out)
for band in [(0,140),(140,281)]:
    print(band, blobs(*band))
figs={'f1':(17,22,84,89),'f2':(115,22,182,89),'f3':(217,23,283,90),'f4':(318,22,385,89),'f5':(415,22,482,89),
      'A':(120,153,187,220),'B':(219,153,285,220),'C':(315,153,382,220),'D':(413,154,480,220)}
ns=[3,4,5,4,3]
def read(b):
    x0,y0,x1,y1=b; xc=(x0+x1)/2; h=(y1-y0)/5; w=(x1-x0)/5
    rows=[]
    for r,n in enumerate(ns):
        yc=y0+h*(r+0.5); row=''
        for j in range(n):
            xc_=xc+(j-(n-1)/2)*w
            v=a[int(yc)-2:int(yc)+3,int(xc_)-2:int(xc_)+3].mean()
            row+='B' if v<120 else 'W'
        rows.append(row)
    return rows
R={k:read(v) for k,v in figs.items()}
for k,v in R.items(): print(k,' '.join(v))
def diff(p,q): return [i for i in range(5) if p[i]!=q[i]]
seq=['f1','f2','f3','f4','f5']
for p,q in zip(seq,seq[1:]):
    d=diff(R[p],R[q]); flips=[all(R[p][i][j]!=R[q][i][j] for j in range(len(R[p][i]))) for i in d]
    print(p,'->',q,'rows differ',d,'full flip',flips)
for o in 'ABCD':
    d=diff(R['f5'],R[o]); flips=[all(R['f5'][i][j]!=R[o][i][j] for j in range(len(R['f5'][i]))) for i in d]
    print('f5 ->',o,'rows differ',d,'full flip',flips)
