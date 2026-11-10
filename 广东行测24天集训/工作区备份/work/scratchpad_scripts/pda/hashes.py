import pymupdf, json, glob, os, re
from PIL import Image
pymupdf.TOOLS.mupdf_display_errors(False)
IDX='/home/user/work/index'
OUT='/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pda/hashes32.json'
def dhash(im, n=32):
    im = im.convert('L').resize((n+1, n), Image.LANCZOS)
    px = list(im.get_flattened_data()) if hasattr(im,"get_flattened_data") else list(im.getdata()); bits = []
    for r in range(n):
        for c in range(n):
            bits.append(1 if px[r*(n+1)+c] > px[r*(n+1)+c+1] else 0)
    return int(''.join(map(str,bits)),2)
res=[]
docs={}
for f in sorted(glob.glob(f'{IDX}/*.json')):
    tag=os.path.basename(f)[:-5]
    qs=json.load(open(f))
    for q in qs:
        if q['kind']!='q' or not q['images'] or q['section'] not in ('判断',None): continue
        path='/home/user/'+q['file']
        if path not in docs: docs[path]=pymupdf.open(path)
        doc=docs[path]; hs=[]
        for (p,bb) in q['images']:
            r=pymupdf.Rect(bb)
            if r.width<40 or r.height<25: continue
            try:
                pix=doc[p].get_pixmap(clip=r, dpi=72)
                im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
                hs.append(dict(p=p,bb=bb,h=dhash(im),ar=round(r.width/r.height,2)))
            except Exception as e: pass
        if hs: res.append(dict(tag=tag,qno=q['qno'],hs=hs))
json.dump(res,open(OUT,'w'))
print(len(res))
