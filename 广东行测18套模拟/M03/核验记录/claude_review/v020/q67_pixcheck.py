import sys, math
from PIL import Image
import numpy as np
# 用法：python3 q67_pixcheck.py [图片路径]；缺省为M03第67题0.2.0题图
path=sys.argv[1] if len(sys.argv)>1 else '/home/user/xing-ce1/广东行测18套模拟/M03/assets/q67_projectile_v020.png'
im=Image.open(path).convert('L')
a=np.array(im)
S=6.0
H,W=a.shape
dark=a<128
# wall mask from svg path M11 69 H137 V165 H129 V78 H11 Z
ys,xs=np.nonzero(dark)
pts=np.stack([xs/S,ys/S],1)
def in_wall(x,y):
    return ((11-0.3<=x<=137+0.3) and (69-0.3<=y<=78+0.3)) or ((129-0.3<=x<=137+0.3) and (69-0.3<=y<=165+0.3))
# distance to parabolas
def dpar(x,y,dx,drop):
    best=1e9
    for i in range(0,401):
        s=i/400
        px=195-dx*s; py=13+drop*s*s
        d=math.hypot(px-x,py-y)
        if d<best: best=d
    return best
# sample curve pixels: exclude wall, O dot (r 2.1 around 195,13), label boxes
lab=[(201,17-9.5*0.75,201+9.5*0.8,17+0.5),(147,26-9.5*0.75,147+9.5*0.7,26+0.5),(154,64-9.5*0.75,154+9.5*0.7,64+0.5)]
def in_lab(x,y):
    return any(b[0]-0.5<=x<=b[2]+0.5 and b[1]-0.5<=y<=b[3]+0.5 for b in lab)
cnt=0; offA=0; offB=0; far=0; maxd=0
idx=np.arange(len(pts))
np.random.seed(0)
sample=np.random.choice(idx,size=min(4000,len(idx)),replace=False)
for k in sample:
    x,y=pts[k]
    if in_wall(x,y) or in_lab(x,y) or math.hypot(x-195,y-13)<2.6: continue
    dA=dpar(x,y,78,56); dB=dpar(x,y,58,71)
    d=min(dA,dB); maxd=max(maxd,d); cnt+=1
    if d>1.0: far+=1
print('curve pixels sampled',cnt,'max dist to nearest new parabola (svg units)',round(maxd,3),'n>1.0 units',far)
# endpoint check: dark pixels nearest to landing points
def nearest_dark(x0,y0,excl_wall=True):
    best=(1e9,None)
    for k in range(len(pts)):
        x,y=pts[k]
        if excl_wall and in_wall(x,y): continue
        d=math.hypot(x-x0,y-y0)
        if d<best[0]: best=(d,(round(x,2),round(y,2)))
    return best
print('nearest non-wall dark px to A landing (117,69):',nearest_dark(117,69))
print('nearest non-wall dark px to B landing (137,84):',nearest_dark(137,84))
