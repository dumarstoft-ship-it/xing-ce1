# Extra Q (ZJ2021-A类-085): which option forms a cuboid together with pieces 1 and 2?
# Step 1: enumerate placements of piece 2 inside the complement of piece 1 in a 4x2x3 box.
# Step 2: render every remaining 10-cube piece in all 24 rotations (same oblique projection as the
#         drawing) and score it against each option drawing.
import sys, itertools
sys.path.insert(0,'/home/user/xing-ce1/广东行测18套模拟/重编/M03/复核/scripts')
from cuberender import render, score
from PIL import Image
import numpy as np
IMG='/home/user/xing-ce1/江浙行测_AI题库/images/original/352.png'
OUT='/tmp/claude-0/-home-user-xing-ce1/532e1442-4812-52b3-a392-6d873e7b4a6c/scratchpad/m03_second_blind_work/'
a=np.array(Image.open(IMG).convert('L'))
P1=[(x,y,0) for x in range(4) for y in range(2)]+[(1,1,1),(3,1,1),(3,1,2)]
P2=[(0,0,0),(1,0,0),(1,0,1)]
def rots():
    out=[]
    for perm in itertools.permutations(range(3)):
        for s in itertools.product((1,-1),repeat=3):
            M=np.zeros((3,3),int)
            for i in range(3): M[i,perm[i]]=s[i]
            if round(np.linalg.det(M))==1: out.append(M)
    return out
ROT=rots()
def norm(S):
    mn=np.min(np.array(list(S)),axis=0)
    return frozenset(tuple(int(c) for c in np.array(v)-mn) for v in S)
def orients(S):
    return {norm([tuple(M.dot(v)) for v in S]) for M in ROT}
def connected(S):
    S=set(S); st=[next(iter(S))]; seen={st[0]}
    while st:
        v=st.pop()
        for d in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
            w=(v[0]+d[0],v[1]+d[1],v[2]+d[2])
            if w in S and w not in seen: seen.add(w); st.append(w)
    return len(seen)==len(S)
box={(x,y,z) for x in range(4) for y in range(2) for z in range(3)}
comp=box-set(P1)
print('complement size',len(comp))
pieces={}
for O in orients(P2):
    for t in itertools.product(range(-3,5),range(-2,3),range(-1,4)):
        pl={(v[0]+t[0],v[1]+t[1],v[2]+t[2]) for v in O}
        if pl<=comp:
            rest=comp-pl
            if connected(rest):
                pieces.setdefault(norm(rest),[]).append(sorted(pl))
print('distinct remaining pieces (up to translation):',len(pieces))
# canonical form up to rotation
def canon(S): return min(tuple(sorted(o)) for o in orients(S))
cands={}
for S,pls in pieces.items():
    cands.setdefault(canon(S),(S,pls))
print('distinct up to rotation:',len(cands))
for k,(S,pls) in cands.items():
    print(' piece2 at',pls[0],' rest:',sorted(S))
# option boxes in the image (x0,y0,x1,y1)
boxes={'A':(15,185,100,330),'B':(135,185,225,330),'C':(255,175,355,330),'D':(380,185,475,330)}
u,d=27.5,9.2
def bbox(m):
    ys,xs=np.where(m); return xs.min(),ys.min(),xs.max(),ys.max()
def fit(S,L):
    x0,y0,x1,y1=boxes[L]; t=a[y0:y1,x0:x1]<110; W,H=x1-x0,y1-y0
    r=np.array(render(S,40,H+80,u,d,(W+200,H+200)))<110
    rb=bbox(r); tb=bbox(t); best=None
    for ax in (0,1):
        for ay in (0,1):
            ox=(tb[0]-rb[0]) if ax==0 else (tb[2]-rb[2]); oy=(tb[1]-rb[1]) if ay==0 else (tb[3]-rb[3])
            for dx in np.arange(-1.5,1.6,0.5):
                for dy in np.arange(-1.5,1.6,0.5):
                    rr=render(S,40+ox+dx,H+80+oy+dy,u,d,(W,H))
                    p,rc=score(t,rr); f=2*p*rc/max(1e-9,p+rc)
                    if best is None or f>best[0]: best=(f,rr)
    return best
if __name__=='__main__':
    for L in 'ABCD':
        res=[]
        for k,(S,pls) in cands.items():
            for O in orients(S):
                f,rr=fit(sorted(O),L)
                res.append((round(f,3),sorted(O)))
        res.sort(reverse=True)
        print(L,'best F',res[0][0],'second',res[1][0] if len(res)>1 else None)
