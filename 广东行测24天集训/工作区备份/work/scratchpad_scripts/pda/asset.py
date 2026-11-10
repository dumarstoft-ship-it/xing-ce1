"""Render a clean question asset: question region at given dpi, white out page headers/footers/watermark lines and
'A.A B.B' option-letter lines, then collapse big blank bands. usage: asset.py tag qno out.png [dpi]"""
import pymupdf, json, sys, re
from PIL import Image, ImageDraw
pymupdf.TOOLS.mupdf_display_errors(False)
PAT = re.compile(r'(第\s*\d+\s*页|共\s*\d+\s*页|^\s*-\s*\d+\s*-\s*$|本试卷由|粉笔|认准淘宝|通关达人|公考,|事业编|一站式备考|网友回忆版|^\s*[A-D]\s*[\.．、]\s*[A-D]\s*$|gwyeasy|公众号|淘宝|资料铺子)')
def render(tag, qno, dpi=200, margin_x=20):
    for q in json.load(open(f'/home/user/work/index/{tag}.json')):
        if q['kind']=='q' and q['qno']==qno: break
    else: raise SystemExit('missing')
    doc = pymupdf.open('/home/user/' + q['file']); s = dpi/72; parts=[]
    for (p, y0, y1) in q['segs']:
        page = doc[p]
        clip = pymupdf.Rect(margin_x, max(0, y0-2), page.rect.width-margin_x, min(page.rect.height, y1+2))
        pix = page.get_pixmap(clip=clip, dpi=dpi)
        im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples); d = ImageDraw.Draw(im)
        def wipe(r):
            rr = pymupdf.Rect(r) & clip
            if rr.is_empty: return
            d.rectangle([(rr.x0-clip.x0)*s-2, (rr.y0-clip.y0)*s-2, (rr.x1-clip.x0)*s+2, (rr.y1-clip.y0)*s+2], fill='white')
        lines=[]
        for b in page.get_text('dict', clip=clip)['blocks']:
            if b.get('type')!=0: continue
            for l in b['lines']:
                lines.append((''.join(sp['text'] for sp in l['spans']), l['bbox']))
        bands=[]
        for t,bb in lines:
            if PAT.search(t) or re.fullmatch(r'\s*[\.．]\s*[A-D]\s*', t): wipe(bb); bands.append((bb[1],bb[3]))
            elif re.fullmatch(r'\s*\d{1,3}\s*', t) and (bb[1] > page.rect.height-70 or bb[3] < 70): wipe(bb)
        for t,bb in lines:
            if re.fullmatch(r'\s*[A-D]\s*', t) and any(abs(bb[1]-y0)<3 and abs(bb[3]-y1)<3 for y0,y1 in bands): wipe(bb)
        # wipe banner-like images (very wide & short) and tiny watermark images
        for img in page.get_images(full=True):
            for r in page.get_image_rects(img[0]):
                if (r.width > 450 and r.height < 35): wipe(r)
        parts.append(im)
    W = max(i.width for i in parts); H = sum(i.height for i in parts)
    c = Image.new('RGB', (W, H), 'white'); y = 0
    for i in parts: c.paste(i, (0, y)); y += i.height
    # collapse blank bands
    g = c.convert('L'); px = g.load(); rows=[]
    for yy in range(c.height):
        dark = 0
        for xx in range(0, c.width, 2):
            if px[xx, yy] < 200: dark += 1
            if dark > 1: break
        rows.append(dark > 1)
    keep=[]; run=0; gap=int(0.12*dpi)
    for yy, r in enumerate(rows):
        if r: run=0; keep.append(yy)
        else:
            run+=1
            if run<=gap: keep.append(yy)
    # drop a thin leading ink run (descenders of the previous line)
    runs=[]; cur=None
    for yy, r in enumerate(rows):
        if r and cur is None: cur=yy
        if not r and cur is not None: runs.append((cur,yy)); cur=None
    if runs and runs[0][1]-runs[0][0] < 0.08*dpi and len(runs)>1:
        for yy in range(runs[0][0], runs[0][1]): rows[yy]=False
        keep=[yy for yy in keep if not (runs[0][0]<=yy<runs[0][1])]
    # trim leading/trailing blanks
    while keep and not rows[keep[0]]: keep.pop(0)
    while keep and not rows[keep[-1]]: keep.pop()
    out = Image.new('RGB', (c.width, len(keep)+2*gap), 'white')
    for i, yy in enumerate(keep): out.paste(c.crop((0, yy, c.width, yy+1)), (0, i+gap))
    # trim horizontal margins
    g2=out.convert('L'); bbox=Image.eval(g2, lambda v: 255 if v<200 else 0).getbbox()
    if bbox: out=out.crop((max(0,bbox[0]-20),0,min(out.width,bbox[2]+20),out.height))
    return out
if __name__=='__main__':
    tag, qno, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]; dpi=int(sys.argv[4]) if len(sys.argv)>4 else 200
    im=render(tag,qno,dpi); im.save(out); print(out, im.size)
