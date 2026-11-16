# Sanity check: rendered pieces 1 and 2 vs. the drawing (extra puzzle)
import sys
sys.path.insert(0,'/home/user/xing-ce1/广东行测18套模拟/重编/M03/复核/scripts')
from cuberender import render, score
from PIL import Image
import numpy as np
IMG='/home/user/xing-ce1/江浙行测_AI题库/images/original/352.png'
a=np.array(Image.open(IMG).convert('L'))
P1=[(x,y,0) for x in range(4) for y in range(2)]+[(1,1,1),(3,1,1),(3,1,2)]
P2=[(0,0,0),(1,0,0),(1,0,1)]
for name,S,bx,org in [('piece1',P1,(70,40,215,155),(77,148.5)),('piece2',P2,(265,75,345,155),(270,148.5))]:
    x0,y0,x1,y1=bx; t=a[y0:y1,x0:x1]<110; W,H=x1-x0,y1-y0
    best=None
    for ox in np.arange(-3,3.1,0.5):
        for oy in np.arange(-2,2.1,0.5):
            for du in (-0.5,0,0.5):
                for dd in (-0.4,0,0.4):
                    rr=render(S,org[0]-x0+ox,org[1]-y0+oy,27.5+du,9.2+dd,(W,H))
                    p,rc=score(t,rr); f=2*p*rc/max(1e-9,p+rc)
                    if best is None or f>best[0]: best=(f,p,rc)
    print(name,'F=%.3f p=%.3f r=%.3f'%best)
