import sys
from PIL import Image, ImageDraw
out=sys.argv[1]; files=sys.argv[2:]
W=1100
ims=[]
for f in files:
    im=Image.open(f).convert('RGB')
    s=min(1.0, W/im.width)
    im=im.resize((int(im.width*s),int(im.height*s)))
    lab=Image.new('RGB',(im.width,28),'white'); d=ImageDraw.Draw(lab); d.text((5,5),f.split('/')[-1],fill=(255,0,0))
    can=Image.new('RGB',(im.width,im.height+28),'white'); can.paste(lab,(0,0)); can.paste(im,(0,28))
    ims.append(can)
H=sum(i.height for i in ims)+10*len(ims)
S=Image.new('RGB',(max(i.width for i in ims),H),'white'); y=0
for i in ims: S.paste(i,(0,y)); y+=i.height+10
S.save(out); print(S.size)
