import pymupdf, sys
from PIL import Image
pymupdf.TOOLS.mupdf_display_errors(False)
path=sys.argv[1]; pages=[int(x) for x in sys.argv[2].split(',')]; out=sys.argv[3]; dpi=int(sys.argv[4]) if len(sys.argv)>4 else 80
clip=None
if len(sys.argv)>5:
    y0,y1=[float(v) for v in sys.argv[5].split(':')]; clip=(y0,y1)
doc=pymupdf.open(path); ims=[]
for p in pages:
    pg=doc[p-1]; r=pg.rect
    c=pymupdf.Rect(0, r.height*clip[0], r.width, r.height*clip[1]) if clip else None
    pix=pg.get_pixmap(dpi=dpi, clip=c); ims.append(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
W=max(i.width for i in ims); H=sum(i.height for i in ims)
cv=Image.new('RGB',(W,H),'white'); y=0
for i in ims: cv.paste(i,(0,y)); y+=i.height
cv.save(out); print(out,cv.size, len(doc))
