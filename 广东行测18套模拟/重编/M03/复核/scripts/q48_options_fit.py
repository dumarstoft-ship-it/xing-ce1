# For each option of Q48, try all 24 proper rotations (and mirror images for info) of the
# main-figure voxel set, render in the same oblique projection and score against the option drawing.
import sys, itertools
sys.path.insert(0,'/home/user/xing-ce1/广东行测18套模拟/重编/M03/复核/scripts')
from cuberender import render, score
from PIL import Image
import numpy as np
P='/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s18_p11_i02.png'
OUT='/tmp/claude-0/-home-user-xing-ce1/532e1442-4812-52b3-a392-6d873e7b4a6c/scratchpad/m03_second_blind_work/'
a=np.array(Image.open(P).convert('L'))
main=[(0,0,0),(0,1,0),(1,1,0),(2,1,0),(0,1,1),(2,1,1),(3,1,1),(0,0,2),(0,1,2),(2,0,2),(2,1,2)]
boxes={'A':(150,10,262,114),'B':(270,8,372,116),'C':(375,8,492,116),'D':(488,8,592,116)}
u,d=20.5,10

def rotations():
    mats=[]
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1,-1),repeat=3):
            M=np.zeros((3,3),int)
            for i in range(3): M[i,perm[i]]=signs[i]
            mats.append(M)
    return mats
ALL=rotations()
ROT=[M for M in ALL if round(np.linalg.det(M))==1]
MIR=[M for M in ALL if round(np.linalg.det(M))==-1]

def transform(S,M):
    P=[tuple(int(c) for c in M.dot(np.array(v))) for v in S]
    mn=np.min(np.array(P),axis=0)
    return [tuple(int(c) for c in (np.array(p)-mn)) for p in P]

def bbox(mask):
    ys,xs=np.where(mask)
    return xs.min(),ys.min(),xs.max(),ys.max()

def fit_option(S, L, verbose=False, save=None):
    x0,y0,x1,y1=boxes[L]
    t=a[y0:y1,x0:x1]<140
    W,H=x1-x0,y1-y0
    tb=bbox(t)
    # render at a provisional origin, get bbox, align bottom-left
    r=np.array(render(S,30,H+60,u,d,(W+200,H+200)))<140
    rb=bbox(r)
    best=None
    for ax in (0,1):  # align left or right edges
        for ay in (0,1):  # align top or bottom
            ox=(tb[0]-rb[0]) if ax==0 else (tb[2]-rb[2])
            oy=(tb[1]-rb[1]) if ay==0 else (tb[3]-rb[3])
            for dx in np.arange(-1.5,1.6,0.5):
                for dy in np.arange(-1.5,1.6,0.5):
                    rr=render(S,30+ox+dx,H+60+oy+dy,u,d,(W,H))
                    p,rc=score(t,rr)
                    f=2*p*rc/max(1e-9,p+rc)
                    if best is None or f>best[0]: best=(f,p,rc,ox+dx,oy+dy,rr)
    if save:
        f,p,rc,ox,oy,rr=best
        rr=np.array(rr)<140
        ov=np.full(t.shape+(3,),255,np.uint8)
        ov[t&rr]=(0,0,0); ov[t&~rr]=(255,0,0); ov[~t&rr]=(0,0,255)
        Image.fromarray(ov).resize((ov.shape[1]*5,ov.shape[0]*5),Image.NEAREST).save(OUT+save)
    return best

if __name__=='__main__':
    for L in 'ABCD':
        res=[]
        for i,M in enumerate(ROT):
            S=transform(main,M)
            f,p,rc,ox,oy,_=fit_option(S,L)
            res.append((f,p,rc,'R%d'%i))
        for i,M in enumerate(MIR):
            S=transform(main,M)
            f,p,rc,ox,oy,_=fit_option(S,L)
            res.append((f,p,rc,'M%d'%i))
        res.sort(reverse=True)
        print(L, ['%s F=%.3f p=%.3f r=%.3f'%(n,f,p,rc) for f,p,rc,n in res[:5]])
