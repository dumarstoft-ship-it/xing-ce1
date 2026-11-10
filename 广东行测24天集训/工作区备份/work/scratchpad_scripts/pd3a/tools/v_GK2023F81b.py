import numpy as np, sys
sys.path.insert(0,'.')
from boxfold import fold
def big(r,c): return {(r,c),(r,c+1),(r+1,c),(r+1,c+1)}
net=set()
for (r,c) in [(0,5),(2,1),(2,3),(2,5),(4,3)]: net|=big(r,c)
flaps={(0,7):((0,1),'右上角小片(→)'),(2,7):((-1,0),'右侧小片(↑)'),(3,0):((0,-1),'左侧小片(←)'),(6,4):((-1,0),'底部小片(↑)')}
net|=set(flaps)
fr=fold(net,(2,2,2))[0]
n=np.array(fr[(0,7)][1]); cen=np.array([1.,1,1])+n
tang=[np.array(t) for t in [(1,0,0),(0,1,0),(0,0,1),(-1,0,0),(0,-1,0),(0,0,-1)] if np.dot(t,n)==0]
target='→↑/↑↓'
for su in tang:
    sv=[t for t in tang if (np.cross(su,-t)==n).all()][0]
    grid={}; who={}
    for f,((dr,dc),name) in flaps.items():
        c,nn,u,v=fr[f]; arrow3=dc*u+dr*v; rel=np.array(c)-cen
        col=0 if np.dot(rel,su)<0 else 1; row=0 if np.dot(rel,sv)<0 else 1
        a=(int(np.dot(arrow3,sv)),int(np.dot(arrow3,su)))
        sym={(0,1):'→',(0,-1):'←',(-1,0):'↑',(1,0):'↓'}[a]
        grid[(row,col)]=sym; who[(row,col)]=name
    pat=grid[(0,0)]+grid[(0,1)]+'/'+grid[(1,0)]+grid[(1,1)]
    if pat==target:
        for k in sorted(who): print(k, who[k], grid[k])
