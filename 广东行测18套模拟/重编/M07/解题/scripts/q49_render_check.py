"""Q49 读图核验: 用斜二测投影把读出的立体渲染出来, 与题图逐像素叠合比对.
- 组合体: 正面图读出16个可见方块; 反面图 = 绕竖直轴转180°. 在包围盒内逐一试加方块, 找出两幅图中都看不到的位置.
- ①②和四个选项同样渲染比对.
用法: python3 q49_render_check.py [输出目录]   (给出目录时保存叠合图: 黑=两者都有线, 红=只有原图, 蓝=只有渲染)
"""
import sys, itertools
from PIL import Image, ImageDraw
import numpy as np
SRC='/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s22_p13_i00.png'
def render(cubes, ox, oy, sx=16.5, sy=16.0, d=7.5, size=(240,128), F=6, lw=3):
    W,H=size; img=Image.new('RGB',(W*F,H*F),'white'); dr=ImageDraw.Draw(img)
    P=lambda x,y,z:((ox+sx*x+d*z)*F,(oy-sy*y-d*z)*F)
    for (x,y,z) in sorted(cubes,key=lambda c:-(c[2]-0.46*(c[0]+c[1]))):
        g=cubes[(x,y,z)]=='g'
        cf,ct,cr=((128,)*3,(175,)*3,(105,)*3) if g else ((255,)*3,(255,)*3,(205,)*3)
        front=[P(x,y+1,z),P(x+1,y+1,z),P(x+1,y,z),P(x,y,z)]
        top=[P(x,y+1,z),P(x,y+1,z+1),P(x+1,y+1,z+1),P(x+1,y+1,z)]
        right=[P(x+1,y+1,z),P(x+1,y+1,z+1),P(x+1,y,z+1),P(x+1,y,z)]
        for poly,c in ((right,cr),(top,ct),(front,cf)):
            dr.polygon(poly,fill=c); dr.line(poly+[poly[0]],fill=(0,0,0),width=lw*F//2)
    return img
def diff(cubes, box, ox, oy, name=None, F=8, **kw):
    src=Image.open(SRC).convert('L').crop(box)
    src=np.array(src.resize((src.width*F,src.height*F),Image.NEAREST))
    r=np.array(render(cubes,ox-box[0],oy-box[1],size=(box[2]-box[0],box[3]-box[1]),F=F,**kw).convert('L'))
    a=src<110; b=r<110
    if name:
        out=np.full(a.shape+(3,),235,np.uint8); out[a&b]=(0,0,0); out[a&~b]=(230,0,0); out[~a&b]=(0,90,255)
        Image.fromarray(out).save(name)
    return round(float((a^b).mean()),3)
W,G='w','g'
H={p:W for p in [(0,0,0),(-2,0,1),(-1,0,1),(1,0,1),(-2,0,2),(-1,0,2),(1,0,2),(-1,1,1),(0,1,1),(0,1,2),(1,1,2),(-1,2,1),(0,2,2)]}
H.update({p:G for p in [(0,1,0),(-2,1,2),(0,0,2)]})
back=lambda S:{(1-x,y,2-z):c for (x,y,z),c in S.items()}
out=sys.argv[1] if len(sys.argv)>1 else None
nm=lambda s:(out+'/'+s) if out else None
print('正面图叠合误差',diff(H,(15,25,115,112),50.5,106,nm('q49_front.png')))
print('反面图叠合误差',diff(back(H),(135,25,235,112),143,99,nm('q49_back.png'),sx=15.75))
def views(S):
    f=np.array(render(S,35.5,81,size=(100,90),F=4).convert('L'))
    b=np.array(render(back(S),8,74,size=(100,90),F=4,sx=15.75).convert('L'))
    return f,b
f0,b0=views(H); hidden=[]
for p in itertools.product(range(-3,3),range(0,4),range(-1,4)):
    if p in H: continue
    S=dict(H); S[p]=W; f,b=views(S)
    if (f!=f0).sum()==0 and (b!=b0).sum()==0: hidden.append(p)
print('两幅图都看不到、可藏第17块的位置:',hidden)
P1={(0,0,0):W,(0,1,0):G,(0,0,1):W,(1,0,1):W,(1,0,2):W}
P2={(0,0,0):W,(0,1,0):G,(1,0,0):W,(1,0,1):W,(1,1,1):W,(1,2,1):W}
print('① 叠合误差',diff(P1,(265,40,345,100),276.5,92.5,nm('q49_p1.png'),sx=15.5,sy=15.5,d=7))
P1b={k:v for k,v in P1.items() if k!=(0,0,1)}
print('   (去掉被挡住的连接块(0,0,1)后误差',diff(P1b,(265,40,345,100),276.5,92.5,None,sx=15.5,sy=15.5,d=7),')')
print('② 叠合误差',diff(P2,(385,30,450,105),394,99.5,nm('q49_p2.png'),sx=15.2,sy=15.2,d=7))
kw=dict(sx=16.5,sy=15.8,d=7.5)
OPT={'A':({(0,0,0):G,(1,0,0):W,(2,0,0):W,(0,1,0):W,(0,2,0):W,(0,1,-1):W},(85,185,170,260),100,252),
     'B':({(0,0,0):G,(1,0,0):W,(-1,1,0):W,(0,1,0):W,(0,2,0):W,(0,1,1):W},(200,190,275,260),226,253.5),
     'C':({(0,0,0):W,(0,1,0):W,(1,0,0):W,(2,0,0):G,(1,0,-1):W,(1,-1,0):W},(325,190,400,262),333.5,239),
     'D':({(0,0,0):W,(1,0,0):G,(2,0,0):W,(0,1,0):W,(0,2,0):W,(0,1,-1):W},(445,185,525,258),460,252)}
for k,(o,box,ox,oy) in OPT.items(): print('选项'+k,'叠合误差',diff(o,box,ox,oy,nm('q49_opt%s.png'%k),**kw))
