"""crop an OCR'd analysis page: ansimg.py TAG PAGE(1-based) y0frac y1frac [scale] -> png path"""
import sys
from PIL import Image
tag,p=sys.argv[1],int(sys.argv[2]); y0,y1=float(sys.argv[3]),float(sys.argv[4]); sc=float(sys.argv[5]) if len(sys.argv)>5 else 0.45
im=Image.open(f'/home/user/work/ocr/{tag}/p{p:03d}.png'); w,h=im.size
c=im.crop((0,int(h*y0),w,int(h*y1))); c=c.resize((int(c.width*sc),int(c.height*sc)))
out=f'/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pd3a/r/ans_{tag}_p{p}_{int(y0*100)}.png'; c.save(out); print(out)
