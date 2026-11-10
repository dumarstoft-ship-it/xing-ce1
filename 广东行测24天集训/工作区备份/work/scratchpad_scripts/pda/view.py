import pymupdf, json, sys, os
from PIL import Image, ImageDraw, ImageFont
pymupdf.TOOLS.mupdf_display_errors(False)
IDX='/home/user/work/index'
def region(tag, qno, dpi=110, margin_x=20):
    for q in json.load(open(f'{IDX}/{tag}.json')):
        if q['kind']=='q' and q['qno']==qno:
            doc=pymupdf.open('/home/user/'+q['file']); ims=[]
            for (p,y0,y1) in q['segs']:
                page=doc[p]
                clip=pymupdf.Rect(margin_x,max(0,y0-2),page.rect.width-margin_x,min(page.rect.height,y1+2))
                pix=page.get_pixmap(clip=clip,dpi=dpi)
                ims.append(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
            W=max(i.width for i in ims); H=sum(i.height for i in ims)
            c=Image.new('RGB',(W,H),'white'); y=0
            for i in ims: c.paste(i,(0,y)); y+=i.height
            return c
    return None
if __name__=='__main__':
    tag=sys.argv[1]; qs=[int(x) for x in sys.argv[2].split(',')]; out=sys.argv[3]; dpi=int(sys.argv[4]) if len(sys.argv)>4 else 110
    ims=[]
    for q in qs:
        im=region(tag,q,dpi)
        if im is None: print('missing',q); continue
        lab=Image.new('RGB',(im.width,22),(255,235,200)); d=ImageDraw.Draw(lab); d.text((5,4),f'{tag}-{q}',fill='black')
        ims+= [lab, im]
    W=max(i.width for i in ims); H=sum(i.height for i in ims)
    c=Image.new('RGB',(W,H),'white'); y=0
    for i in ims: c.paste(i,(0,y)); y+=i.height
    c.save(out); print(out, c.size)
