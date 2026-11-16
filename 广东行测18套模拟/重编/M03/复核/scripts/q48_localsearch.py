# Local search: modify voxel set (add/remove single cubes) to best reproduce an option drawing.
import sys
sys.path.insert(0,'/home/user/xing-ce1/广东行测18套模拟/重编/M03/复核/scripts')
from q48_options_fit import main, ROT, MIR, transform, fit_option, boxes, a, u, d
from cuberender import render, score
import numpy as np
from PIL import Image
OUT='/tmp/claude-0/-home-user-xing-ce1/532e1442-4812-52b3-a392-6d873e7b4a6c/scratchpad/m03_second_blind_work/'
NB=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
def F(S,L,ox,oy):
    x0,y0,x1,y1=boxes[L]; t=a[y0:y1,x0:x1]<140
    W,H=x1-x0,y1-y0
    rr=render(S,30+ox,H+60+oy,u,d,(W,H))
    p,rc=score(t,rr); return 2*p*rc/max(1e-9,p+rc), rr, t
def search(S,L,ox,oy,iters=30):
    S=set(S); cur,_,_=F(S,L,ox,oy)
    for it in range(iters):
        best=(cur,None)
        cands=set()
        for v in S:
            for dl in NB:
                w=(v[0]+dl[0],v[1]+dl[1],v[2]+dl[2])
                if w not in S: cands.add(('add',w))
            cands.add(('rem',v))
        for op,w in cands:
            T=set(S)
            if op=='add': T.add(w)
            else: T.discard(w)
            if not T: continue
            f,_,_=F(T,L,ox,oy)
            if f>best[0]+1e-4: best=(f,(op,w))
        if best[1] is None: break
        op,w=best[1]
        if op=='add': S.add(w)
        else: S.discard(w)
        cur=best[0]
        print('  ',op,w,'F=%.4f'%cur)
    return S,cur
if __name__=='__main__':
    L=sys.argv[1]; kind=sys.argv[2]; idx=int(sys.argv[3])
    M=(ROT if kind=='R' else MIR)[idx]
    S0=transform(main,M)
    f,p,rc,ox,oy,_=fit_option(S0,L)
    print(L,kind,idx,'start F=%.4f'%f,'offset',ox,oy)
    S,cur=search(S0,L,ox,oy)
    print('final F=%.4f'%cur, sorted(S))
    print('added', sorted(set(S)-set(S0)), 'removed', sorted(set(S0)-set(S)))
    f,rr,t=F(S,L,ox,oy)
    rr=np.array(rr)<140
    ov=np.full(t.shape+(3,),255,np.uint8)
    ov[t&rr]=(0,0,0); ov[t&~rr]=(255,0,0); ov[~t&rr]=(0,0,255)
    Image.fromarray(ov).resize((ov.shape[1]*5,ov.shape[0]*5),Image.NEAREST).save(OUT+'q48_ls_%s_%s%d.png'%(L,kind,idx))
