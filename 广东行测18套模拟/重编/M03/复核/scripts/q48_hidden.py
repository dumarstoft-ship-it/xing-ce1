import sys
sys.path.insert(0,'/home/user/xing-ce1/广东行测18套模拟/重编/M03/复核/scripts')
from cuberender import render
import numpy as np
main=[(0,0,0),(0,1,0),(1,1,0),(2,1,0),(0,1,1),(2,1,1),(3,1,1),(0,0,2),(0,1,2),(2,0,2),(2,1,2)]
X0,Y0,u,d=60,140,20.5,10
base=np.array(render(main,X0,Y0,u,d,(220,200)))<140
hidden=[]
for x in range(-2,6):
    for y in range(-2,7):
        for z in range(-2,5):
            p=(x,y,z)
            if p in main: continue
            r=np.array(render(main+[p],X0,Y0,u,d,(220,200)))<140
            diff=(r^base).sum()
            if diff<=4:
                hidden.append(p)
print(len(hidden))
print(sorted(hidden))
# hidden & face-adjacent to main
adj=[p for p in hidden if any((abs(p[0]-q[0])+abs(p[1]-q[1])+abs(p[2]-q[2]))==1 for q in main)]
print('adjacent hidden', sorted(adj))
