# Oblique-projection polycube renderer used to test voxel hypotheses for Q48 / Q49.
# Screen mapping: X = X0 + u*x + d*y ; Y = Y0 - u*z - d*y   (x right, y back, z up)
from PIL import Image, ImageDraw
import numpy as np

def faces_of(v, S):
    x,y,z=v
    fs=[]
    # front face (y-)
    if (x,y-1,z) not in S: fs.append(('F',[(x,y,z),(x+1,y,z),(x+1,y,z+1),(x,y,z+1)]))
    # top face (z+)
    if (x,y,z+1) not in S: fs.append(('T',[(x,y,z+1),(x+1,y,z+1),(x+1,y+1,z+1),(x,y+1,z+1)]))
    # right face (x+)
    if (x+1,y,z) not in S: fs.append(('R',[(x+1,y,z),(x+1,y+1,z),(x+1,y+1,z+1),(x+1,y,z+1)]))
    return fs

def render(S, X0, Y0, u, d, size, scale=4, lw=2.0):
    W,H=size
    im=Image.new('L',(W*scale,H*scale),255)
    dr=ImageDraw.Draw(im)
    S=set(S)
    # painter: depth along view dir (-d/u, 1, -d/u)
    k=d/u
    order=sorted(S, key=lambda v: -(v[1]-k*v[0]-k*v[2]))
    def P(p):
        x,y,z=p
        return ((X0+u*x+d*y)*scale, (Y0-u*z-d*y)*scale)
    for v in order:
        for name,poly in faces_of(v,S):
            pts=[P(p) for p in poly]
            dr.polygon(pts, fill=255)
            dr.line(pts+[pts[0]], fill=0, width=max(1,int(round(lw*scale))))
    return im.resize((W,H), Image.LANCZOS)

def score(target_dark, rendered):
    r=np.array(rendered)<140
    t=target_dark
    from scipy import ndimage
    td=ndimage.binary_dilation(t, iterations=1)
    rd=ndimage.binary_dilation(r, iterations=1)
    prec=(r & td).sum()/max(1,r.sum())
    rec=(t & rd).sum()/max(1,t.sum())
    return prec, rec
