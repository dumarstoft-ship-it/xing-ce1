"""Render science question regions (stem + figure + options) at 200 dpi into out/PD-C/assets, compressing long blank bands."""
import json, sys, os
import pymupdf
from PIL import Image
import numpy as np
pymupdf.TOOLS.mupdf_display_errors(False)
OUT = '/home/user/work/out/PD-C/assets'
os.makedirs(OUT, exist_ok=True)

def region(tag, qno):
    for q in json.load(open(f'/home/user/work/index/{tag}.json')):
        if q['kind'] == 'q' and q['qno'] == qno: return q
    raise KeyError((tag, qno))

def render(q, dpi=200, margin_x=20):
    doc = pymupdf.open('/home/user/' + q['file'])
    ims = []
    for (p, y0, y1) in q['segs']:
        page = doc[p]
        clip = pymupdf.Rect(margin_x, max(0, y0 - 2), page.rect.width - margin_x, min(page.rect.height, y1 + 2))
        pix = page.get_pixmap(clip=clip, dpi=dpi)
        ims.append(Image.frombytes('RGB', (pix.width, pix.height), pix.samples))
    W = max(i.width for i in ims); H = sum(i.height for i in ims)
    can = Image.new('RGB', (W, H), 'white'); y = 0
    for i in ims: can.paste(i, (0, y)); y += i.height
    return can

def squeeze(im, max_blank=40, keep=24, thr=245):
    a = np.asarray(im.convert('L'))
    blank = (a > thr).all(axis=1)
    rows = []; run = 0
    for r, b in enumerate(blank):
        run = run + 1 if b else 0
        if not b or run <= keep: rows.append(r)
    a3 = np.asarray(im)[rows]
    out = Image.fromarray(a3)
    # trim trailing/leading blank rows and right blank columns
    g = np.asarray(out.convert('L')); cols = np.where((g <= thr).any(axis=0))[0]; rws = np.where((g <= thr).any(axis=1))[0]
    if len(cols) and len(rws):
        out = out.crop((max(0, cols[0] - 10), max(0, rws[0] - 10), min(out.width, cols[-1] + 10), min(out.height, rws[-1] + 10)))
    return out

if __name__ == '__main__':
    for spec in sys.argv[1:]:
        iid, tag, qno = spec.split(':')
        q = region(tag, int(qno))
        im = squeeze(render(q))
        fn = f'{OUT}/{iid}_{tag}-{qno}.png'
        im.save(fn, optimize=True)
        print(fn, im.size)
