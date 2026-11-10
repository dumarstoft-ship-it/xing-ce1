import numpy as np, sys
sys.path.insert(0,'.')
from boxfold import fold
def big(r,c): return {(r,c),(r,c+1),(r+1,c),(r+1,c+1)}
net=set()
for (r,c) in [(0,5),(2,1),(2,3),(2,5),(4,3)]: net|=big(r,c)
flaps={(0,7):(0,1),(2,7):(-1,0),(3,0):(0,-1),(6,4):(-1,0)}   # arrow (drow,dcol) in image
net|=set(flaps)
print(len(net))
res=fold(net,(2,2,2))
print('valid foldings',len(res))
fr=res[0]
# find the face holding the flaps
ns=set(tuple(fr[f][1]) for f in flaps); print('flap normals',ns)
n=np.array(list(ns)[0])
# screen frame for that face seen from outside: pick any u perpendicular; we will compare all 4 rotations anyway
tang=[np.array(t) for t in [(1,0,0),(0,1,0),(0,0,1),(-1,0,0),(0,-1,0),(0,0,-1)] if np.dot(t,n)==0]
pats=set()
for su in tang:
    sv=None
    for t in tang:
        if (np.cross(su,-t)==n).all(): sv=t
    # face center
    cen=np.array([1.0,1.0,1.0])+n*1.0
    grid={}
    for f,(dr,dc) in flaps.items():
        c,nn,u,v=fr[f]
        arrow3=dc*u+dr*v
        rel=np.array(c)-cen
        col=0 if np.dot(rel,su)<0 else 1; row=0 if np.dot(rel,sv)<0 else 1
        a=(int(np.dot(arrow3,sv)),int(np.dot(arrow3,su)))  # (down, right)
        name={(0,1):'→',(0,-1):'←',(-1,0):'↑',(1,0):'↓'}[a]
        grid[(row,col)]=name
    pats.add(grid[(0,0)]+grid[(0,1)]+'/'+grid[(1,0)]+grid[(1,1)])
print(pats)
opts={'A':'→↓/↑←','B':'→↑/↑↓','C':'↑←/↓↓','D':'→←/↑←'}
for k,v in opts.items(): print(k,v,'MATCH' if v in pats else '-')
