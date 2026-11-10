import sys
from PIL import Image
src,y0,y1,out=sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),sys.argv[4]
im=Image.open(src); W,H=im.size
c=im.crop((0,int(H*y0),W,int(H*y1)))
c.save(out); print(out,c.size)
