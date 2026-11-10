import pymupdf, sys, json
pymupdf.TOOLS.mupdf_display_errors(False)
# usage: crop.py tag qno out dpi [imgindex|all]  -> renders the image bboxes of the question (union of listed images on same page) 
tag, qno, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]; dpi=int(sys.argv[4]) if len(sys.argv)>4 else 200
for q in json.load(open(f'/home/user/work/index/{tag}.json')):
    if q['kind']=='q' and q['qno']==qno:
        doc=pymupdf.open('/home/user/'+q['file'])
        ims=[(p,bb) for p,bb in q['images'] if (bb[2]-bb[0])>60 and (bb[3]-bb[1])>30]
        from PIL import Image
        parts=[]
        for p,bb in ims:
            pix=doc[p].get_pixmap(clip=pymupdf.Rect(bb[0]-3,bb[1]-3,bb[2]+3,bb[3]+3),dpi=dpi)
            parts.append(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
        W=max(i.width for i in parts); H=sum(i.height for i in parts)
        c=Image.new('RGB',(W,H),'white'); y=0
        for i in parts: c.paste(i,(0,y)); y+=i.height
        c.save(out); print(out,c.size)
