# Direct check: piece (a) = complement of P1 and P2-placement {(3,0,1),(2,0,1),(2,1,1)} in the 4x2x3 box,
# rotated by the cyclic map (x,y,z)->(x_D=y, y_D=z-1, z_D=x), rendered against option D (and the
# manually read voxel sets of A, B, C against their own drawings, as a sanity check of the reading).
import sys
sys.path.insert(0,'/home/user/xing-ce1/广东行测18套模拟/重编/M03/复核/scripts')
from cuberender import render, score
from PIL import Image
import numpy as np
IMG='/home/user/xing-ce1/江浙行测_AI题库/images/original/352.png'
OUT='/tmp/claude-0/-home-user-xing-ce1/532e1442-4812-52b3-a392-6d873e7b4a6c/scratchpad/m03_second_blind_work/'
a=np.array(Image.open(IMG).convert('L'))
P1=[(x,y,0) for x in range(4) for y in range(2)]+[(1,1,1),(3,1,1),(3,1,2)]
box={(x,y,z) for x in range(4) for y in range(2) for z in range(3)}
P2a={(3,0,1),(2,0,1),(2,1,1)}
rest=box-set(P1)-P2a
print('rest',len(rest),sorted(rest))
D=[(y,z-1,x) for (x,y,z) in rest]
print('mapped to D frame',sorted(D))
boxes={'A':(15,185,100,330),'B':(135,185,225,330),'C':(255,175,355,330),'D':(380,185,475,330)}
read={'A':[(0,0,1),(0,0,2),(0,1,1),(0,1,2),(0,1,3),(1,1,3),(1,1,2),(1,1,1),(1,1,0),(1,0,0)],
      'B':[(0,0,0),(1,0,0),(1,0,1),(1,0,2),(1,0,3),(0,1,0),(0,1,1),(0,1,2),(0,1,3),(1,1,0),(1,1,1),(1,1,2),(1,1,3)],
      'C':[(x,0,z) for x in range(2) for z in range(4)]+[(1,1,3),(1,2,3)],
      'D':sorted(D)}
origin={'A':(19.5,322),'B':(142,322),'C':(266,322),'D':(391,322)}
u,dd=27.5,9.2
for L in 'ABCD':
    x0,y0,x1,y1=boxes[L]; t=a[y0:y1,x0:x1]<110; W,H=x1-x0,y1-y0
    best=None
    for ox in np.arange(-2,2.1,0.5):
        for oy in np.arange(-2,2.1,0.5):
            for du in (-0.5,0,0.5):
                for ddd in (-0.4,0,0.4):
                    rr=render(read[L],origin[L][0]-x0+ox,origin[L][1]-y0+oy,u+du,dd+ddd,(W,H))
                    p,rc=score(t,rr); f=2*p*rc/max(1e-9,p+rc)
                    if best is None or f>best[0]: best=(f,p,rc,rr)
    f,p,rc,rr=best
    print(L,'cubes',len(read[L]),'F=%.3f p=%.3f r=%.3f'%(f,p,rc))
    r2=np.array(rr)<110
    ov=np.full(t.shape+(3,),255,np.uint8)
    ov[t&r2]=(0,0,0); ov[t&~r2]=(255,0,0); ov[~t&r2]=(0,0,255)
    Image.fromarray(ov).resize((ov.shape[1]*4,ov.shape[0]*4),Image.NEAREST).save(OUT+'x1_read_%s.png'%L)
