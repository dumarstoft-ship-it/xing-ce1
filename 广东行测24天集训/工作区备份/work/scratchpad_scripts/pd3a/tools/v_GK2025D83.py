import numpy as np
from PIL import Image
S='/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pd3a'
a=np.asarray(Image.open(f'{S}/stage/GK2025D-83.png').convert('L')).astype(int)
# figure grid boxes: x ranges approx (65-240),(262-435),(458-632),(650-825),(838-1012),(1032-1205); y 112-285
xs=[(66,238),(262,436),(458,632),(651,825),(840,1013),(1033,1206)]
y0,y1=113,285
grids=[]
for (x0,x1) in xs:
    g=np.zeros((5,5),int)
    for r in range(5):
        for c in range(5):
            x=x0+(c+0.5)*(x1-x0)/5; y=y0+(r+0.5)*(y1-y0)/5
            g[r,c]=1 if a[int(y)-3:int(y)+4,int(x)-3:int(x)+4].mean()<100 else 0
    grids.append(g)
def axes(g):
    pts={(r,c) for r in range(5) for c in range(5) if g[r,c]}
    out=[]
    # reflections: vertical axis c->k-c, horizontal r->k-r, diag (r,c)->(c,r) shifted, anti
    for k in range(0,9):
        if {(r,k-c) for r,c in pts}==pts: out.append(('V',k/2))
        if {(k-r,c) for r,c in pts}==pts: out.append(('H',k/2))
    for k in range(-4,5):
        if {(c-k,r+k) for r,c in pts}==pts: out.append(('D',k))   # reflect across c-r=k
    for k in range(0,9):
        if {(k-c,k-r) for r,c in pts}==pts: out.append(('A',k))   # across r+c=k
    return pts,out
def on_axis(pts,ax):
    t,k=ax
    if t=='V': return sum(1 for r,c in pts if c==k)
    if t=='H': return sum(1 for r,c in pts if r==k)
    if t=='D': return sum(1 for r,c in pts if c-r==k)
    if t=='A': return sum(1 for r,c in pts if r+c==k)
for i,g in enumerate(grids,1):
    pts,ax=axes(g)
    print(i, ''.join(''.join('#' if v else '.' for v in row)+'/' for row in g), 'black',len(pts),'axes',ax,'on-axis',[on_axis(pts,x) for x in ax])
