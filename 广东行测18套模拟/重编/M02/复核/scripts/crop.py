import sys
from PIL import Image
# usage: crop.py src out x0 y0 x1 y1 scale
src,out=sys.argv[1],sys.argv[2]
x0,y0,x1,y1=map(int,sys.argv[3:7])
s=int(sys.argv[7]) if len(sys.argv)>7 else 3
im=Image.open(src).crop((x0,y0,x1,y1))
im=im.resize((im.width*s,im.height*s),Image.NEAREST)
im.save(out)
