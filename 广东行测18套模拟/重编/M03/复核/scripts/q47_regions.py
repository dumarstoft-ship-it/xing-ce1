# Q47: count black connected parts and enclosed white regions in each cell / option
from PIL import Image
import numpy as np
from scipy import ndimage
P='/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s18_p11_i01.png'
im=np.array(Image.open(P).convert('L'))
dark=im<140
H,W=im.shape
def groups(idx):
    g=[]
    for v in idx:
        if g and v-g[-1][-1]<=2: g[-1].append(v)
        else: g.append([v])
    return [(a[0],a[-1]) for a in g]
# grid lines
colfrac=dark[0:300].mean(axis=0)
rowfrac=dark[:, 50:350].mean(axis=1)
print('vlines', groups([x for x in range(W) if colfrac[x]>0.8]))
print('hlines', groups([y for y in range(H) if rowfrac[y]>0.8]))
rowfrac2=dark[:, 0:400].mean(axis=1)
print('hlines opt', groups([y for y in range(320,H) if rowfrac2[y]>0.5]))
colfrac2=dark[330:415].mean(axis=0)
print('vlines opt', groups([x for x in range(W) if colfrac2[x]>0.8]))

cells={}
xs=[(52,148),(152,247),(251,347)]
ys=[(10,98),(104,198),(204,298)]
for r in range(3):
    for c in range(3):
        if r==2 and c==2: continue
        cells[f'r{r+1}c{c+1}']=(xs[c][0],ys[r][0],xs[c][1],ys[r][1])
oxs=[(9,100),(106,197),(203,294),(300,391)]
for i,L in enumerate('ABCD'):
    cells['opt'+L]=(oxs[i][0],333,oxs[i][1],427)
for thr in (140,200):
  print('threshold',thr)
  for k,(x0,y0,x1,y1) in cells.items():
    sub=np.array(Image.open(P).convert('L'))[y0:y1,x0:x1]<thr
    labB,nB=ndimage.label(sub, structure=np.ones((3,3)))
    sizes=ndimage.sum(sub,labB,range(1,nB+1))
    nBig=sum(1 for s in sizes if s>15)
    labW,nW=ndimage.label(~sub)  # 4-connectivity for white
    # regions touching border are outside
    border=set(np.unique(np.concatenate([labW[0,:],labW[-1,:],labW[:,0],labW[:,-1]])))
    wsizes=ndimage.sum(~sub,labW,range(1,nW+1))
    inner=[(i+1,int(s)) for i,s in enumerate(wsizes) if (i+1) not in border and s>3]
    print(k,'black parts',nBig,[int(s) for s in sizes if s>15],'enclosed regions',len(inner),sorted([s for _,s in inner]))
