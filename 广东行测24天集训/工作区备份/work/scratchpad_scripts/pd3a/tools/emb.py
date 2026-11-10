"""extract embedded images overlapping a question's region: emb.py TAG QNO OUTPREFIX"""
import pymupdf, json, sys
pymupdf.TOOLS.mupdf_display_errors(False)
tag,qno,out=sys.argv[1],int(sys.argv[2]),sys.argv[3]
q=[x for x in json.load(open(f'/home/user/work/index/{tag}.json')) if x['kind']=='q' and x['qno']==qno][0]
doc=pymupdf.open('/home/user/'+q['file'])
k=0
for (p,y0,y1) in q['segs']:
    page=doc[p]
    for info in page.get_image_info(xrefs=True):
        bb=pymupdf.Rect(info['bbox'])
        if bb.y1>y0 and bb.y0<y1 and info['xref']:
            pix=pymupdf.Pixmap(doc,info['xref'])
            if pix.n-pix.alpha>=4: pix=pymupdf.Pixmap(pymupdf.csRGB,pix)
            fn=f'{out}_{k}.png'; pix.save(fn); print(fn, pix.width, pix.height, [round(v,1) for v in bb]); k+=1
