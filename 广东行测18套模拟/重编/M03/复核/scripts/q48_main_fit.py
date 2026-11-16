import sys
sys.path.insert(0,'/home/user/xing-ce1/广东行测18套模拟/重编/M03/复核/scripts')
from cuberender import render, score
from PIL import Image
import numpy as np
P='/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s18_p11_i02.png'
OUT='/tmp/claude-0/-home-user-xing-ce1/532e1442-4812-52b3-a392-6d873e7b4a6c/scratchpad/m03_second_blind_work/'
a=np.array(Image.open(P).convert('L'))
box=(20,12,138,112)
t=a[box[1]:box[3],box[0]:box[2]]<140
main=[(0,0,0),(0,1,0),(1,1,0),(2,1,0),(0,1,1),(2,1,1),(3,1,1),(0,0,2),(0,1,2),(2,0,2),(2,1,2)]
def fit(S, name, X0=25.5, Y0=103.5, u=20.5, d=10):
    best=None
    for dx in np.arange(-1.5,1.6,0.5):
        for dy in np.arange(-1.5,1.6,0.5):
            for du in (-0.5,0,0.5):
                for dd in (-0.5,0,0.5):
                    r=render(S, X0+dx-box[0], Y0+dy-box[1], u+du, d+dd, (box[2]-box[0], box[3]-box[1]))
                    p,rc=score(t,r)
                    f=2*p*rc/(p+rc)
                    if best is None or f>best[0]: best=(f,p,rc,dx,dy,du,dd,r)
    f,p,rc,dx,dy,du,dd,r=best
    print(name,'F=%.3f prec=%.3f rec=%.3f'%(f,p,rc),'shift',dx,dy,du,dd)
    # overlay: red = target only, blue = render only, black = both
    rr=np.array(r)<140
    ov=np.full(t.shape+(3,),255,np.uint8)
    ov[t&rr]=(0,0,0); ov[t&~rr]=(255,0,0); ov[~t&rr]=(0,0,255)
    Image.fromarray(ov).resize((ov.shape[1]*6,ov.shape[0]*6),Image.NEAREST).save(OUT+name+'.png')
    return best
if __name__=='__main__':
    fit(main,'q48_main_fit')
