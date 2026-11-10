# crop.py SRC y0frac y1frac OUT [scale]
import sys
from PIL import Image
src,y0,y1,out=sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),sys.argv[4]
sc=float(sys.argv[5]) if len(sys.argv)>5 else 0.6
im=Image.open(src); W,H=im.size
c=im.crop((0,int(H*y0),W,int(H*y1)))
c=c.resize((int(c.width*sc),int(c.height*sc)),Image.LANCZOS)
c.save(out); print(out,c.size)
