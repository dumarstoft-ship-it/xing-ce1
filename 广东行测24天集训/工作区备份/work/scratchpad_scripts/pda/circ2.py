import numpy as np
from PIL import Image, ImageDraw
im=Image.open('r/gd23z46_raw.png').convert('L')
def mask(box):
    c=im.crop(box); b=(np.array(c)<140)
    # exterior flood fill
    m=Image.fromarray((~b).astype(np.uint8)*255)
    arr0=np.array(m)
    seed=None
    for (x,y) in [(3,3),(c.width-4,3),(3,c.height-4),(c.width-4,c.height-4),(c.width//2,3),(c.width//2,c.height-4)]:
        if arr0[y,x]==255: seed=(x,y); break
    ImageDraw.floodfill(m,seed,128)
    # also fill other exterior seeds
    for (x,y) in [(3,3),(c.width-4,3),(3,c.height-4),(c.width-4,c.height-4),(c.width//2,3),(c.width//2,c.height-4),(3,c.height//2),(c.width-4,c.height//2)]:
        if np.array(m)[y,x]==255: ImageDraw.floodfill(m,(x,y),128)
    arr=np.array(m)
    interior=(arr!=128)  # includes outline pixels
    return interior, b
def fitcircle(outline):
    ys,xs=np.nonzero(outline); pts=np.stack([xs,ys],1).astype(float)
    best=None
    cx0,cy0=pts.mean(0)
    for cx in np.arange(cx0-40,cx0+40,1.0):
        for cy in np.arange(cy0-40,cy0+40,1.0):
            d=np.hypot(pts[:,0]-cx,pts[:,1]-cy)
            hist=np.bincount(np.round(d).astype(int))
            r=hist.argmax(); s=hist[max(0,r-1):r+2].sum()
            if best is None or s>best[0]: best=(s,cx,cy,r)
    return best
boxes={'G':(0,16,146,148),'A':(152,16,280,147),'B':(286,16,413,147),'C':(419,16,546,147),'D':(553,16,680,147)}
M={}; 
for k,b in boxes.items():
    inter,outl=mask(b); f=fitcircle(outl); M[k]=(inter,f); print(k,'circle',f[1:],'area',inter.sum())
# compose
g,(s,gx,gy,gr)=M['G']
R=int(gr)+3
def centered(inter,cx,cy):
    canvas=np.zeros((2*R+1,2*R+1),bool)
    ys,xs=np.nonzero(inter)
    for y,x in zip(ys,xs):
        X=int(round(x-cx))+R; Y=int(round(y-cy))+R
        if 0<=X<2*R+1 and 0<=Y<2*R+1: canvas[Y,X]=True
    return canvas
G=centered(g,gx,gy)
yy,xx=np.mgrid[-R:R+1,-R:R+1]; disk=(np.hypot(xx,yy)<=gr)
for k in 'ABCD':
    inter,(s,cx,cy,r)=M[k]
    O=centered(inter,cx,cy)
    best=None
    for th in range(0,360,2):
        Oi=Image.fromarray(O.astype(np.uint8)*255).rotate(th,resample=Image.NEAREST)
        Or=np.array(Oi)>0
        ov=(G&Or).sum(); un=((G|Or)&disk).sum()/disk.sum()
        score=ov/ disk.sum()
        if best is None or (un-score)>best[0]: best=(un-score,th,un,score)
    print(k,'r=%d'%r,'best rot',best[1],'coverage=%.3f overlap=%.3f'%(best[2],best[3]))
