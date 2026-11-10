"""zoom.py IMG x0 y0 x1 y1 [scale] [out]: crop & upscale (nearest for pixel inspection unless scale<0 -> lanczos)"""
import sys
from PIL import Image
f=sys.argv[1]; x0,y0,x1,y1=map(int,sys.argv[2:6]); s=float(sys.argv[6]) if len(sys.argv)>6 else 4
out=sys.argv[7] if len(sys.argv)>7 else 'r/zoom.png'
im=Image.open(f).convert('RGB').crop((x0,y0,x1,y1))
im=im.resize((int(im.width*abs(s)),int(im.height*abs(s))),Image.LANCZOS if s<0 else Image.NEAREST); im.save(out); print(out,im.size)
