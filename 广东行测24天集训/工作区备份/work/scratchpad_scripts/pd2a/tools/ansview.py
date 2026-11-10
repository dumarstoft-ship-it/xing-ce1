import sys
from PIL import Image
tag,p,f0,f1=sys.argv[1],int(sys.argv[2]),float(sys.argv[3]),float(sys.argv[4])
out=sys.argv[5] if len(sys.argv)>5 else '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pd2a/v/ans.png'
im=Image.open(f'/home/user/work/ocr/{tag}/p{p:03d}.png'); w,h=im.size
c=im.crop((0,int(h*f0),w,int(h*f1)))
c=c.resize((w//2,c.height//2)); c.save(out); print(out, c.size)
