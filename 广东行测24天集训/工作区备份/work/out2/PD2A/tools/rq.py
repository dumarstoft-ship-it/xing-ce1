"""Render a question cleanly: python3 rq.py TAG QNO OUTPNG [dpi] [--keep-opts] [--raw]"""
import sys, json, re, pymupdf, numpy as np
from PIL import Image
pymupdf.TOOLS.mupdf_display_errors(False)
IDX='/home/user/work/index'
def load(tag): return json.load(open(f'{IDX}/{tag}.json'))
JUNK=re.compile(r'^\s*[-－—]?\s*\d{1,3}\s*[-－—]?\s*$|第\s*\d+\s*页|共\s*\d+\s*页|公务员录用考试|公务员考试|粉笔|本试卷由|认准|淘宝|网友回忆版|通关达人|^\s*\d+\s*/\s*\d+\s*$|资料库|一站式备考')
def lines_in(page, y0, y1):
    d=page.get_text('dict', clip=pymupdf.Rect(0,y0,page.rect.width,y1))
    out=[]
    for b in d['blocks']:
        for l in b.get('lines',[]):
            t=''.join(s['text'] for s in l['spans']).strip()
            if t: out.append((l['bbox'], t))
    return out
def is_optline(t):
    tt=t.replace(' ','').replace('　','')
    return bool(re.match(r'^A[\.、．]\s*A?\s*B[\.、．]', tt) or re.match(r'^A[\.、．](A|如上图)', tt) or re.match(r'^[A-D][\.、．]([A-D]|如上图所示)$', tt) or re.match(r'^A[\.、．]AB[\.、．]BC', tt))
def render(tag, qno, out, dpi=200, keep_opts=False, raw=False, collapse=True):
    q=[x for x in load(tag) if x['kind']=='q' and x['qno']==qno][0]
    doc=pymupdf.open('/home/user/'+q['file'])
    ims=[]
    sc=dpi/72
    for (p,y0,y1) in q['segs']:
        page=doc[p]
        L=lines_in(page,y0,y1)
        nxt=[bb[1] for bb,t in L if re.match(r'^\s*%d\s*[、\.．]'%(qno+1), t) and bb[1]>y0+15]
        if nxt: y1=min(y1,min(nxt)-2)
        if not keep_opts:
            cuts=[bb[1] for bb,t in L if is_optline(t)]
            if cuts and min(cuts)>y0+15: y1=min(y1,min(cuts)-1)
        x0c=15; clip=pymupdf.Rect(x0c, max(0,y0-2), page.rect.width-15, min(page.rect.height,y1+2))
        pix=page.get_pixmap(clip=clip,dpi=dpi)
        im=np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).copy()
        for bb,t in L:
            if JUNK.search(t):
                ya=int((bb[1]-clip.y0)*sc)-4; yb=int((bb[3]-clip.y0)*sc)+4
                im[max(0,ya):max(0,yb), :] = 255
        ims.append(im)
    W=max(i.shape[1] for i in ims)
    ims=[np.pad(i,((0,0),(0,W-i.shape[1]),(0,0)),constant_values=255) for i in ims]
    a=np.concatenate(ims,0)
    if not raw:
        g=a.mean(2)
        a[g>212]=255
    if collapse:
        rowblank=(a.mean(2)>=250).all(1)
        keep=[]; run=0
        for i,bl in enumerate(rowblank):
            run = run+1 if bl else 0
            if run<=int(0.12*dpi): keep.append(i)
        a=a[keep]
    m=(a.mean(2)<245); ys,xs=np.where(m)
    if len(ys): a=a[max(0,ys.min()-8):ys.max()+9, max(0,xs.min()-8):xs.max()+9]
    Image.fromarray(a).save(out)
    return out
if __name__=='__main__':
    tag,qno,out=sys.argv[1],int(sys.argv[2]),sys.argv[3]
    dpi=int(sys.argv[4]) if len(sys.argv)>4 and sys.argv[4].isdigit() else 200
    print(render(tag,qno,out,dpi,'--keep-opts' in sys.argv,'--raw' in sys.argv))
