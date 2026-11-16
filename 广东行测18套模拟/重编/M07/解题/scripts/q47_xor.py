"""Q47: 九宫格, 每行 图1与图2叠加、去同存异得图3(相同的线条/颜色消失, 不同处留下并为黑).
第三行: 把方框按两条对角线和两条中线分成8个三角形, 读每个三角形的颜色, 再与选项比对."""
from PIL import Image
import numpy as np
IMG='/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s22_p12_i00.png'
im=np.array(Image.open(IMG).convert('L')).astype(float); b=im<128
def bbox(x0,y0,x1,y1):
    ys,xs=np.nonzero(b[y0:y1,x0:x1]); return x0+xs.min(),y0+ys.min(),x0+xs.max(),y0+ys.max()
NAMES=['上左','上右','右上','右下','下右','下左','左下','左上']
def sectors(bx):
    x0,y0,x1,y1=bx; cx,cy=(x0+x1)/2,(y0+y1)/2
    tri=[[(x0,y0),(cx,y0)],[(cx,y0),(x1,y0)],[(x1,y0),(x1,cy)],[(x1,cy),(x1,y1)],
         [(x1,y1),(cx,y1)],[(cx,y1),(x0,y1)],[(x0,y1),(x0,cy)],[(x0,cy),(x0,y0)]]
    out=set()
    for n,t in zip(NAMES,tri):
        gx=(t[0][0]+t[1][0]+cx)/3; gy=(t[0][1]+t[1][1]+cy)/3
        if im[int(gy)-2:int(gy)+3,int(gx)-2:int(gx)+3].mean()<100: out.add(n)
    return out
f1=sectors(bbox(55,205,144,293)); f2=sectors(bbox(155,205,244,293))
print('第三行图1黑色:',sorted(f1),' 图2黑色:',sorted(f2))
want=f1^f2
print('去同存异(只留不同处,为黑; 两图共有的方框和线条消失):',sorted(want))
optB=sectors(bbox(106,333,193,418)); optC=sectors(bbox(203,333,291,418))
print('选项B(带方框):',sorted(optB),' 选项C(带方框):',sorted(optC))
# 选项A、D无方框, 只有两个黑三角: 用ASCII核对形状
for k,(x0,y0,x1,y1) in {'A':(10,335,95,385),'D':(302,335,388,385)}.items():
    print('选项'+k+'(无方框):')
    for y in range(y0,y1,4): print('   '+''.join('#' if im[y,x]<128 else '.' for x in range(x0,x1,2)))
print('结论: A = 上左(直角在右上的三角)+右上(直角在右下的三角), 与去同存异结果一致且无方框;'
      ' C黑色位置相同但保留了公共的方框线条; D = 左上+上右; B = 上左+下右.')
