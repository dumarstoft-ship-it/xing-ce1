import sys
from PIL import Image, ImageDraw
out=sys.argv[1]; ims=[Image.open(p) for p in sys.argv[2:]]
mx=int(sys.argv[0] and 1100)
rs=[]
for p,i in zip(sys.argv[2:],ims):
    if i.width>mx: i=i.resize((mx,int(i.height*mx/i.width)))
    lab=Image.new('RGB',(i.width,20),(255,235,200)); ImageDraw.Draw(lab).text((4,3),p.split('/')[-1],fill='black'); rs+=[lab,i]
W=max(i.width for i in rs); H=sum(i.height for i in rs); c=Image.new('RGB',(W,H),'white'); y=0
for i in rs: c.paste(i,(0,y)); y+=i.height
c.save(out); print(out,c.size)
