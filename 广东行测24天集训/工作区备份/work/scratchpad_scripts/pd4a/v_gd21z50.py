"""GD2021Z-50: rotate each option back (90° CW) and compare its border colours with the board just outside the '?' patch"""
from PIL import Image
import numpy as np
from scipy import ndimage as nd
im=Image.open('emb/GD2021Z-50_0.png').convert('L'); a=np.asarray(im).astype(int)
def cls(v): return 'D' if v<100 else ('G' if v<200 else 'W')
# --- patch polygon: the white quadrilateral containing '?' on the board (x<290)
board=a[:, :290]
w=board>225
lab,n=nd.label(w)
# choose the white component whose bbox contains the '?' glyph (dark pixels inside a white region) -> largest white comp that is not a hexagon: use bbox aspect
best=None
for i in range(1,n+1):
    ys,xs=np.where(lab==i)
    if len(ys)<300: continue
    bw=xs.max()-xs.min(); bh=ys.max()-ys.min()
    if bw>1.6*bh: best=(i,xs.min(),xs.max(),ys.min(),ys.max(),len(ys))
print('patch comp',best)
i,x0,x1,y0,y1,_=best
m=nd.binary_fill_holes(lab==i)
# corner estimates
rows=[(y,np.where(m[y])[0]) for y in range(y0,y1+1)]
print('top row x-range',rows[1][1].min(),rows[1][1].max(),' bottom row x-range',rows[-2][1].min(),rows[-2][1].max(),' y',y0,y1)
# --- options: find 4 shapes in right part (x>300)
right=a[:, 300:]
nz=right<235
lab2,n2=nd.label(nd.binary_fill_holes(nz))
objs=[]
for j in range(1,n2+1):
    ys,xs=np.where(lab2==j)
    if len(ys)>800: objs.append((xs.min()+300,xs.max()+300,ys.min(),ys.max(),j))
objs.sort()
print('options',objs)
res={}
for name,(ox0,ox1,oy0,oy1,j) in zip('ABCD',objs):
    sub=a[oy0:oy1+1, ox0:ox1+1]; msk=(lab2==j)[oy0:oy1+1, ox0-300:ox1+1-300]
    # rotate 90° clockwise to patch orientation
    subr=np.rot90(sub,-1); mr=np.rot90(msk,-1)
    H=y1-y0+1; W=x1-x0+1
    imr=np.asarray(Image.fromarray(subr.astype('uint8')).resize((W,H),Image.NEAREST)).astype(int)
    mrr=np.asarray(Image.fromarray((mr*255).astype('uint8')).resize((W,H),Image.NEAREST))>127
    # compare along the patch boundary: for boundary pixels of m, take the board pixel 3px outside (along outward normal approx via dilation) and option pixel 3px inside
    er=nd.binary_erosion(m,iterations=4); ring_in=m&~nd.binary_erosion(m,iterations=7)&nd.binary_erosion(m,iterations=3)
    out_ring=nd.binary_dilation(m,iterations=6)&~nd.binary_dilation(m,iterations=3)
    ok=tot=0; detail={}
    ys,xs=np.where(ring_in)
    for y,x in zip(ys,xs):
        # nearest outside ring pixel
        yy0,yy1=max(0,y-9),min(board.shape[0],y+10); xx0,xx1=max(0,x-9),min(board.shape[1],x+10)
        oy,ox=np.where(out_ring[yy0:yy1,xx0:xx1])
        if not len(oy): continue
        d=(oy+yy0-y)**2+(ox+xx0-x)**2; k=d.argmin()
        cb=cls(board[oy[k]+yy0, ox[k]+xx0])
        py,px=y-y0,x-x0
        if not (0<=py<H and 0<=px<W) or not mrr[py,px]: continue
        co=cls(imr[py,px])
        tot+=1; ok+= (cb==co)
        detail[(cb,co)]=detail.get((cb,co),0)+1
    res[name]=(ok,tot,round(ok/max(1,tot),2),detail)
    Image.fromarray(imr.astype('uint8')).resize((W*4,H*4),Image.NEAREST).save(f'r/gd21z50_opt{name}_rot.png')
for k,v in res.items(): print(k,v)
