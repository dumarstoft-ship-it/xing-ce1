import sys
from PIL import Image, ImageDraw
out=sys.argv[1]; files=sys.argv[2:]
ims=[]
for f in files:
    im=Image.open(f).convert('RGB')
    w=1200; h=int(im.height*w/im.width); im=im.resize((w,h))
    lab=Image.new('RGB',(w,26),'yellow'); ImageDraw.Draw(lab).text((5,5),f.split('/')[-1],fill='black')
    ims+= [lab,im]
H=sum(i.height for i in ims); c=Image.new('RGB',(1200,H),'white'); y=0
for i in ims: c.paste(i,(0,y)); y+=i.height
c.save(out); print(out,c.size)
