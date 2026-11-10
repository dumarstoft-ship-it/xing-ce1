"""Extract raw (non-NFKC) text of a question region and render a crop.
usage: qx.py <tag> <qno> [outdir]"""
import pymupdf, json, sys, os
pymupdf.TOOLS.mupdf_display_errors(False)
from PIL import Image
IDX='/home/user/work/index'
def get(tag,qno):
    for q in json.load(open(f'{IDX}/{tag}.json')):
        if q['kind']=='q' and q['qno']==qno: return q
def raw(q):
    doc=pymupdf.open('/home/user/'+q['file'])
    out=[]
    for (p,y0,y1) in q['segs']:
        page=doc[p]
        r=pymupdf.Rect(0,max(0,y0-1),page.rect.width,min(page.rect.height,y1+1))
        out.append(page.get_text('text',clip=r))
    return '\n'.join(out)
def crop(q,out,dpi=150):
    doc=pymupdf.open('/home/user/'+q['file'])
    ims=[]
    for (p,y0,y1) in q['segs']:
        page=doc[p]
        clip=pymupdf.Rect(15,max(0,y0-3),page.rect.width-15,min(page.rect.height,y1+3))
        pix=page.get_pixmap(clip=clip,dpi=dpi)
        ims.append(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
    W=max(i.width for i in ims);H=sum(i.height for i in ims)
    c=Image.new('RGB',(W,H),'white');y=0
    for i in ims: c.paste(i,(0,y)); y+=i.height
    c.save(out); return out
if __name__=='__main__':
    tag,qno=sys.argv[1],int(sys.argv[2])
    q=get(tag,qno)
    print(raw(q))
    if len(sys.argv)>3:
        os.makedirs(sys.argv[3],exist_ok=True)
        print(crop(q,f'{sys.argv[3]}/{tag}_q{qno}.png'))
