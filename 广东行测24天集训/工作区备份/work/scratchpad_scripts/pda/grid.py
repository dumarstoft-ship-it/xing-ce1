import sys
from PIL import Image
import numpy as np
im=np.array(Image.open(sys.argv[1]).convert('L')).astype(float)
H,W=im.shape
dark=im<128
# find panel borders: columns/rows that are mostly dark lines
colsum=dark.sum(0); rowsum=dark.sum(1)
def runs(mask):
    out=[];s=None
    for i,v in enumerate(mask):
        if v and s is None: s=i
        if not v and s is not None: out.append((s,i)); s=None
    if s is not None: out.append((s,len(mask)))
    return out
print('W,H',W,H)
# vertical lines: columns where dark count > 0.3*panel height in a band; do per row band
for band in [(0,int(H*0.5)),(int(H*0.5),H)]:
    sub=dark[band[0]:band[1]]
    cs=sub.sum(0); vl=[ (a+b)//2 for a,b in runs(cs>0.6*(band[1]-band[0])*0.8)]
    rs=sub.sum(1); hl=[ (a+b)//2+band[0] for a,b in runs(rs>0.3*W)]
    print('band',band,'vlines',vl,'hlines',hl)
