# Q49: render my reconstruction of the polyhedron / pieces in the same oblique
# projection as the problem figure, to compare against the original picture.
from PIL import Image, ImageDraw
import sys

S=16.0; D=7.5   # front-face size and oblique offset (pixels), measured from the figure

def proj(x,y,z):
    return (x*S + y*D, -z*S - y*D)

def render(cubes, scale=4, pad=10):
    # cubes: dict (x,y,z)->'w'/'g'
    # painter's order: far to near along view dir v=(-D/S, 1, -D/S)
    k=D/S
    order=sorted(cubes, key=lambda c: -( -k*c[0] + c[1] - k*c[2]))
    polys=[]
    for (x,y,z) in order:
        col=cubes[(x,y,z)]
        front=[proj(x,y,z),proj(x+1,y,z),proj(x+1,y,z+1),proj(x,y,z+1)]
        top=[proj(x,y,z+1),proj(x+1,y,z+1),proj(x+1,y+1,z+1),proj(x,y+1,z+1)]
        right=[proj(x+1,y,z),proj(x+1,y+1,z),proj(x+1,y+1,z+1),proj(x+1,y,z+1)]
        if col=='g':
            fc=(128,128,128); tc=(150,150,150); rc=(100,100,100)
        else:
            fc=(255,255,255); tc=(255,255,255); rc=(210,210,210)
        polys.append((front,fc)); polys.append((top,tc)); polys.append((right,rc))
    xs=[p[0] for poly,_ in polys for p in poly]; ys=[p[1] for poly,_ in polys for p in poly]
    minx,miny=min(xs),min(ys); maxx,maxy=max(xs),max(ys)
    W=int((maxx-minx)*scale)+2*pad; H=int((maxy-miny)*scale)+2*pad
    im=Image.new('RGB',(W,H),'white'); dr=ImageDraw.Draw(im)
    for poly,c in polys:
        pts=[((px-minx)*scale+pad,(py-miny)*scale+pad) for px,py in poly]
        dr.polygon(pts,fill=c,outline=(0,0,0))
        dr.line(pts+[pts[0]],fill=(0,0,0),width=max(1,scale//2))
    return im

def rot180(cubes):
    return {(-x,-y,z):c for (x,y,z),c in cubes.items()}

# Reconstructed polyhedron (front-view coordinates: X right, Y away from viewer, Z up)
POLY={
 (2,0,0):'w',(0,1,0):'w',(1,1,0):'w',(2,1,0):'w',(3,1,0):'w',
 (0,2,0):'w',(1,2,0):'w',(2,2,0):'g',(3,2,0):'w',
 (2,0,1):'g',(1,1,1):'w',(2,1,1):'w',(0,2,1):'g',(2,2,1):'w',(3,2,1):'w',
 (1,1,2):'w',(2,2,2):'w',
}
P1={(0,0,0):'w',(0,0,1):'g',(0,1,0):'w',(1,1,0):'w',(1,2,0):'w'}
P2={(0,0,0):'w',(0,0,1):'g',(1,0,0):'w',(1,1,0):'w',(1,1,1):'w',(1,1,2):'w'}
OPT={
 'A':{(0,0,0):'g',(0,0,1):'w',(0,0,2):'w',(0,-1,1):'w',(1,0,0):'w',(2,0,0):'w'},
 'B':{(0,0,0):'g',(0,0,1):'w',(0,0,2):'w',(-1,0,1):'w',(1,0,0):'w',(0,1,1):'w'},
 'C':{(0,0,0):'w',(1,0,0):'g',(0,-1,0):'w',(0,0,-1):'w',(-1,0,0):'w',(-1,0,1):'w'},
 'D':{(0,0,0):'w',(0,0,1):'w',(0,0,2):'w',(0,-1,1):'w',(1,0,0):'g',(2,0,0):'w'},
}
if __name__=='__main__':
    out=sys.argv[1] if len(sys.argv)>1 else '.'
    render(POLY).save(out+'/r_front.png')
    render(rot180(POLY)).save(out+'/r_back.png')
    render(P1).save(out+'/r_p1.png'); render(P2).save(out+'/r_p2.png')
    for k,v in OPT.items(): render(v).save(out+'/r_opt%s.png'%k)
    print('ok', len(POLY), sum(1 for c in POLY.values() if c=='g'))
