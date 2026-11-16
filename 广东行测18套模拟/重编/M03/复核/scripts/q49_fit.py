# Q49: verify reconstructed polycube (16 white + 6 gray) against the drawing, list hidden cells,
# then compute the section by the plane through P(0,3,3), Q(3,3,3), R(3,0,0).
import sys, itertools
sys.path.insert(0,'/home/user/xing-ce1/广东行测18套模拟/重编/M03/复核/scripts')
from cuberender2 import render, classes
from PIL import Image
import numpy as np
P='/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s18_p12_i00.png'
OUT='/tmp/claude-0/-home-user-xing-ce1/532e1442-4812-52b3-a392-6d873e7b4a6c/scratchpad/m03_second_blind_work/'
a=np.array(Image.open(P).convert('L'))
box=(22,22,122,113)   # avoid the letters P,Q,R as far as possible
t=classes(a[box[1]:box[3],box[0]:box[2]])
C={}
full=[(x,y,z) for x in range(3) for y in range(3) for z in range(3)]
missing={(0,0,2),(1,0,2),(2,0,2),(2,1,2),(1,0,1),(2,0,1),(0,0,0)}
for v in full:
    if v not in missing: C[v]='w'
for v in [(2,2,2),(1,1,2),(0,0,1),(2,1,1),(1,0,0)]: C[v]='g'
C[(1,-1,0)]='w'; C[(3,1,0)]='g'
print('cubes',len(C),'gray',sum(1 for c in C.values() if c=='g'))
def agree(C,X0=25,Y0=103.5,u=20,dx=8,dy=8):
    best=None
    for ox in np.arange(-1.5,1.6,0.5):
        for oy in np.arange(-1.5,1.6,0.5):
            for du in (-0.5,0,0.5):
                for dd in (-0.5,0,0.5):
                    r=classes(render(C,X0+ox-box[0],Y0+oy-box[1],u+du,dx+dd,dy+dd,(box[2]-box[0],box[3]-box[1])))
                    acc=(r==t).mean()
                    # line-tolerant accuracy: ignore pixels adjacent to lines in either image
                    from scipy import ndimage
                    near=ndimage.binary_dilation((r==0)|(t==0),iterations=1)
                    acc2=((r==t)|near).mean()
                    if best is None or acc2>best[0]: best=(acc2,acc,ox,oy,du,dd,r)
    return best
b=agree(C)
print('agreement (line tolerant) %.4f raw %.4f'%(b[0],b[1]), 'params',b[2:6])
r=b[6]
ov=np.full(t.shape+(3,),255,np.uint8)
ov[(t==1)&(r==1)]=(150,150,150); ov[(t==0)&(r==0)]=(0,0,0)
ov[(t!=r)&(t==0)]=(255,0,0); ov[(t!=r)&(r==0)]=(0,0,255)
ov[(t==1)&(r==2)]=(255,180,0); ov[(t==2)&(r==1)]=(0,200,0)
Image.fromarray(ov).resize((ov.shape[1]*6,ov.shape[0]*6),Image.NEAREST).save(OUT+'q49_fit.png')
# hidden cells: adding a cube there (either colour) does not change the picture
_,_,ox,oy,du,dd,_=b
def img(Cx): return classes(render(Cx,25+ox-box[0],103.5+oy-box[1],20+du,8+dd,8+dd,(box[2]-box[0],box[3]-box[1])))
base=img(C)
hid=[]
for v in itertools.product(range(-2,5),range(-2,5),range(-1,4)):
    if v in C: continue
    for col in 'wg':
        Cx=dict(C); Cx[v]=col
        if (img(Cx)!=base).sum()<=3: hid.append((v,col))
print('hidden-capable cells', sorted(set(v for v,c in hid)))
# which cubes of C are invisible (removing them changes nothing)
inv=[v for v in C if (img({k:c for k,c in C.items() if k!=v})!=base).sum()<=3]
print('cubes of C that are invisible', sorted(inv))
# section by plane y=z
sec=[(v,C[v]) for v in C if v[1]==v[2]]
print('section cells (x, k=y=z, colour):', sorted(((v[0],v[1]),c) for v,c in sec))
for k in (2,1,0):
    print('row k=%d:'%k, ' '.join(C.get((x,k,k),'_') for x in range(-1,4)))
