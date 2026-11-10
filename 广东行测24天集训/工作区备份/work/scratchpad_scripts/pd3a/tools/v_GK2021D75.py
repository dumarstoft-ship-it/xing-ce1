import sys; sys.path.insert(0,'/home/user/work/out2/PD2A/tools')
import numpy as np
from PIL import Image
from scipy import ndimage as nd
from cube import *
S='/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pd3a'
a=np.asarray(Image.open(f'{S}/h/emb_GK2021D-75_0.png').convert('L')).astype(float)
print(a.shape)
# given cube
sub=a[5:125,0:110]
m=sub<200
lab,k=nd.label(nd.binary_closing(m,iterations=2))
sizes=nd.sum(m,lab,range(1,k+1)); i=1+int(np.argmax(sizes))
C=cube_corners(nd.binary_fill_holes(lab==i))
print(C)
obs={'front':sample_gray(sub,C['FTL'],C['FTR'],C['FBL'],10,0.1),
     'top':sample_gray(sub,C['TBL'],C['RTB'],C['FTL'],10,0.1),
     'right':sample_gray(sub,C['FTR'],C['RTB'],C['FBR'],10,0.1)}
for f in obs: print(f); print(pr(obs[f]))
nets={}
for name,(x0,x1) in {'A':(170,330),'B':(350,505),'C':(528,682),'D':(705,857)}.items():
    cells,cs=detect_net(a,x0,5,x1,125)
    print(name,cs,sorted(cells))
    nets[name]={k:sample_gray(a,*v,10,0.1) for k,v in cells.items()}
np.save(f'{S}/h/GK2021D75_obs.npy',obs,allow_pickle=True)
for name,net in nets.items():
    if len(net)!=6: print(name,'net cells',len(net)); continue
    print(name)
    check_gray(net,{'given':obs})
