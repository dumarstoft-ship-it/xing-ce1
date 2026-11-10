from PIL import Image, ImageDraw
def render(cells, U=92, OX=45, OY=-45, X0=40, Y0=365, W=480, H=420, path=None):
    """cells: dict (x,y,z)->'B'/'W'"""
    def P(x,y,z): return (X0+U*x+OX*y, Y0-U*z+OY*y)
    im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    col={'B':{'f':(90,90,90),'t':(120,120,120),'r':(70,70,70)},'W':{'f':(255,255,255),'t':(255,255,255),'r':(205,205,205)}}
    for (x,y,z) in sorted(cells,key=lambda c:(-c[1],c[0],c[2])):
        c=col[cells[(x,y,z)]]
        f=[P(x,y,z),P(x+1,y,z),P(x+1,y,z+1),P(x,y,z+1)]
        t=[P(x,y,z+1),P(x+1,y,z+1),P(x+1,y+1,z+1),P(x,y+1,z+1)]
        r=[P(x+1,y,z),P(x+1,y+1,z),P(x+1,y+1,z+1),P(x+1,y,z+1)]
        for poly,k in ((r,'r'),(t,'t'),(f,'f')):
            d.polygon(poly,fill=c[k]); d.line(poly+[poly[0]],fill=(0,0,0),width=4)
    if path: im.save(path)
    return im
if __name__=='__main__':
    import sys, json
    from PIL import Image
    cells={tuple(json.loads(k)):v for k,v in json.loads(sys.argv[1]).items()}
    crop=[int(v) for v in sys.argv[2].split(',')]
    X0=int(sys.argv[3]); a=render(cells,X0=X0)
    src=Image.open('../r/z_gd19x35.png').convert('RGB').crop(crop)
    cv=Image.new('RGB',(src.width+20+a.width,max(src.height,a.height)),'white'); cv.paste(src,(0,0)); cv.paste(a,(src.width+20,0)); cv.save(sys.argv[4]); print('ok')
