# Refined fit (exclude frame lines, finer offsets, small scale variation)
import sys
sys.path.insert(0,'/home/user/xing-ce1/广东行测18套模拟/重编/M03/复核/scripts')
import q48_options_fit as Q
from cuberender import render, score
import numpy as np
from PIL import Image
OUT='/tmp/claude-0/-home-user-xing-ce1/532e1442-4812-52b3-a392-6d873e7b4a6c/scratchpad/m03_second_blind_work/'
Q.boxes.update({'A':(152,10,262,114),'B':(272,9,370,116),'C':(377,9,490,116),'D':(489,9,589,116)})
def refit(S,L,save=None):
    x0,y0,x1,y1=Q.boxes[L]; t=Q.a[y0:y1,x0:x1]<140; W,H=x1-x0,y1-y0
    f,p,rc,ox,oy,_=Q.fit_option(S,L)
    best=None
    for du in (-0.5,0,0.5):
        for dd in (-0.5,0,0.5):
            for dx in np.arange(-1.5,1.51,0.25):
                for dy in np.arange(-1.5,1.51,0.25):
                    rr=render(S,30+ox+dx,H+60+oy+dy,Q.u+du,Q.d+dd,(W,H))
                    p,rc=score(t,rr); f=2*p*rc/max(1e-9,p+rc)
                    if best is None or f>best[0]: best=(f,p,rc,rr)
    if save:
        rr=np.array(best[3])<140
        ov=np.full(t.shape+(3,),255,np.uint8)
        ov[t&rr]=(0,0,0); ov[t&~rr]=(255,0,0); ov[~t&rr]=(0,0,255)
        Image.fromarray(ov).resize((ov.shape[1]*5,ov.shape[0]*5),Image.NEAREST).save(OUT+save)
    return best[:3]
if __name__=='__main__':
    Dset=[(0,0,3),(0,1,1),(0,1,2),(0,1,3),(1,1,0),(1,1,1),(1,1,3),(2,0,1),(2,0,3),(2,1,1),(2,1,3)]
    print('D fitted set', refit(Dset,'D','q48_D_refit.png'))
    print('D = R20(main)?', sorted(Q.transform(Q.main,Q.ROT[20])))
    print('D set        ', sorted(Dset))
