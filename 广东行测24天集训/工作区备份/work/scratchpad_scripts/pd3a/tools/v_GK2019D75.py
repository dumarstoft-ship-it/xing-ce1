import sys; sys.path.insert(0,'/home/user/work/out2/PD2A/tools')
import numpy as np
from PIL import Image
from cube import *
S='/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pd3a'
a=np.asarray(Image.open(f'{S}/h/emb_GK2019D-75_0.png').convert('L')).astype(float)
V=[22.5,40.5,57.5,75,92.5]; H=[24.5,43.5,62.5,81.5]
cells=[(1,1),(0,3),(1,0),(1,2),(1,3),(2,1)]
net={}
for (r,c) in cells:
    TL=(V[c]+1.5,H[r]+1.5); TR=(V[c+1]-1.5,H[r]+1.5); BL=(V[c]+1.5,H[r+1]-1.5)
    net[(r,c)]=sample_quad(a,TL,TR,BL,n=12,margin=0.04)
for k,v in net.items(): print(k); print(show_bm(v))
# options
xr={'A':(141,205),'B':(228,296),'C':(326,394),'D':(423,492)}
opts={}
for name,(x0,x1) in xr.items():
    sub=a[18:90,x0:x1]
    m=sub<200
    from scipy import ndimage as nd
    lab,k=nd.label(nd.binary_closing(m,iterations=2))
    sizes=nd.sum(m,lab,range(1,k+1)); i=1+int(np.argmax(sizes))
    C=cube_corners(nd.binary_fill_holes(lab==i))
    print(name,C)
    opts[name]={'front':sample_quad(sub,C['FTL'],C['FTR'],C['FBL'],12,0.08),
                'top':sample_quad(sub,C['TBL'],C['RTB'],C['FTL'],12,0.08),
                'right':sample_quad(sub,C['FTR'],C['RTB'],C['FBR'],12,0.08)}
    for f in ('front','top','right'): print(name,f); print(show_bm(opts[name][f]))
res=check_soft(net,opts,sigma=1.0,topk=3)
