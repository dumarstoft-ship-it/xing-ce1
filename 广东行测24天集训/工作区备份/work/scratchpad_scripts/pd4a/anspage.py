"""anspage.py ANS_TAG PAGE(1-based) [y0frac y1frac] [dpi] : render (part of) a scanned analysis page from the source PDF"""
import sys, json, pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
tag=sys.argv[1]; p=int(sys.argv[2])
y0=float(sys.argv[3]) if len(sys.argv)>3 else 0; y1=float(sys.argv[4]) if len(sys.argv)>4 else 1
dpi=int(sys.argv[5]) if len(sys.argv)>5 else 130
meta=json.load(open(f'/home/user/work/ocr/{tag}/_meta.json'))
doc=pymupdf.open('/home/user/'+meta['file']); pg=doc[p-1]
r=pg.rect; clip=pymupdf.Rect(0,r.height*y0,r.width,r.height*y1)
pix=pg.get_pixmap(clip=clip,dpi=dpi); out=f'r/ans_{tag}_p{p}_{int(y0*100)}_{int(y1*100)}.png'; pix.save(out); print(out,pix.width,pix.height)
