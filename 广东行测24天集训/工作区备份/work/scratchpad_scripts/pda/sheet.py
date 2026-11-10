import json, sys
from PIL import Image, ImageDraw
recs=[json.loads(l) for l in open('/home/user/work/out/PD-A/questions.jsonl')]
lo,hi=int(sys.argv[1]),int(sys.argv[2]); out=sys.argv[3]
ims=[]
for r in recs[lo:hi]:
    im=Image.open('/home/user/work/out/PD-A/'+r['assets'][0]); w=560
    im=im.resize((w,int(im.height*w/im.width)))
    lab=Image.new('RGB',(w,18),(220,235,255)); ImageDraw.Draw(lab).text((3,2),r['id']+' '+r['source']['paper']+'-'+str(r['source']['qno']),fill='black')
    ims+=[lab,im]
# two columns
colh=[0,0]; cols=[[],[]]
for i in range(0,len(ims),2):
    c=0 if colh[0]<=colh[1] else 1
    cols[c]+= [ims[i],ims[i+1]]; colh[c]+=ims[i].height+ims[i+1].height
H=max(colh); cv=Image.new('RGB',(1130,H),'white')
for c in range(2):
    y=0
    for im in cols[c]: cv.paste(im,(c*570,y)); y+=im.height
cv.save(out); print(out,cv.size)
