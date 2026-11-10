import sys; sys.path.insert(0,'/home/user/work/out2/PD2A/tools')
import numpy as np
from PIL import Image
from cube import *
S='/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pd3a'
a=np.asarray(Image.open(f'{S}/h/emb_GK2021D-75_0.png').convert('L')).astype(float)
obs=np.load(f'{S}/h/GK2021D75_obs.npy',allow_pickle=True).item()
grids={'A':([178,213.5,249,285,320],[13,48,84,119.5]),'B':([355.5,391,427,462,498],[13,48.5,84,119.5]),
       'C':([533,569,604.5,640,676],[13,48.5,84,119.5]),'D':([711,746,782,817.5,853],[13,48.5,84,119.5])}
cells=[(1,2),(0,2),(1,0),(1,1),(1,3),(2,2)]
for name,(V,H) in grids.items():
    net={}
    for (r,c) in cells:
        TL=(V[c]+1.5,H[r]+1.5); TR=(V[c+1]-1.5,H[r]+1.5); BL=(V[c]+1.5,H[r+1]-1.5)
        net[(r,c)]=sample_gray(a,TL,TR,BL,10,0.1)
    print('==',name)
    res=check_gray(net,{'given':obs},verbose=False)
    print(res['given'])
