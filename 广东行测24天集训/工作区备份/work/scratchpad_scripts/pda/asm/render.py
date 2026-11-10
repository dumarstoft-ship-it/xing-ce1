from PIL import Image, ImageDraw
U=135; OX,OY=70,-37
def P(x,y,z,X0,Y0): return (X0+U*x+OX*y, Y0-U*z+OY*y)
def render(cells, X0=98, Y0=540, W=600, H=575, path=None, fill=(255,255,255)):
    im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    for (x,y,z) in sorted(cells,key=lambda c:(-c[1],c[0],c[2])):
        f=[P(x,y,z,X0,Y0),P(x+1,y,z,X0,Y0),P(x+1,y,z+1,X0,Y0),P(x,y,z+1,X0,Y0)]
        t=[P(x,y,z+1,X0,Y0),P(x+1,y,z+1,X0,Y0),P(x+1,y+1,z+1,X0,Y0),P(x,y+1,z+1,X0,Y0)]
        r=[P(x+1,y,z,X0,Y0),P(x+1,y+1,z,X0,Y0),P(x+1,y+1,z+1,X0,Y0),P(x+1,y,z+1,X0,Y0)]
        for poly in (r,t,f):
            d.polygon(poly,fill=fill,outline=(0,0,0)); d.line(poly+[poly[0]],fill=(0,0,0),width=5)
    if path: im.save(path)
    return im
if __name__=='__main__':
    import sys, json
    C=[(-1,2,2),(0,2,2),(0,1,2),(0,0,1),(1,0,1),(1,1,1),(1,0,0),(1,1,0),(0,1,1),(0,2,1)]
    a=render(C); b=Image.open('../r/z_gd20x43_oC.png').convert('RGB')
    cv=Image.new('RGB',(1210,575),'white'); cv.paste(b,(0,0)); cv.paste(a,(610,0)); cv.save('cmpC.png')
