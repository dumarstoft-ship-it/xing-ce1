# Colored oblique polycube renderer (white/gray cubes) for Q49.
from PIL import Image, ImageDraw
import numpy as np
def faces_of(v,S):
    x,y,z=v; fs=[]
    if (x,y-1,z) not in S: fs.append([(x,y,z),(x+1,y,z),(x+1,y,z+1),(x,y,z+1)])
    if (x,y,z+1) not in S: fs.append([(x,y,z+1),(x+1,y,z+1),(x+1,y+1,z+1),(x,y+1,z+1)])
    if (x+1,y,z) not in S: fs.append([(x+1,y,z),(x+1,y+1,z),(x+1,y+1,z+1),(x+1,y,z+1)])
    return fs
def render(C, X0, Y0, u, dx, dy, size, scale=4, lw=2.0):
    """C: dict voxel->'w'/'g'. dx,dy: screen offset per unit depth (X += dx*y, Y -= dy*y)"""
    W,H=size
    im=Image.new('L',(W*scale,H*scale),255)
    dr=ImageDraw.Draw(im)
    S=set(C)
    k1=dx/u; k2=dy/u
    order=sorted(S,key=lambda v: -(v[1]-k1*v[0]-k2*v[2]))
    def P(p):
        x,y,z=p
        return ((X0+u*x+dx*y)*scale,(Y0-u*z-dy*y)*scale)
    for v in order:
        col=150 if C[v]=='g' else 255
        for poly in faces_of(v,S):
            pts=[P(p) for p in poly]
            dr.polygon(pts,fill=col)
            dr.line(pts+[pts[0]],fill=0,width=max(1,int(round(lw*scale))))
    return im.resize((W,H),Image.LANCZOS)
def classes(arr):
    a=np.asarray(arr)
    c=np.full(a.shape,2,np.int8)   # 2 = white
    c[a<200]=1                     # 1 = gray fill
    c[a<100]=0                     # 0 = line
    return c
