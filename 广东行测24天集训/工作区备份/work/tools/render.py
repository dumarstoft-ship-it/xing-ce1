"""Render a question / material region (or a full page) of a source PDF to PNG.
Usage:
  python3 render.py q   <tag> <qno> [outdir] [dpi]      e.g. render.py q GD2025 71
  python3 render.py m   <tag> <material_id> [outdir]    e.g. render.py m GK2024F GK2024F-M3
  python3 render.py page <tag> <page_no_0based> [outdir] [dpi]
  python3 render.py ans <tag> <keyword-regex>            -> prints analysis text around matches
Tags are index file names under /home/user/work/index (xing-ce1 files have no suffix, xingce files end with _xc).
Returns the PNG paths. Multi-page regions produce one PNG per page segment (stitched vertically into one file too).
"""
import pymupdf, json, sys, os, re, unicodedata
from PIL import Image
pymupdf.TOOLS.mupdf_display_errors(False)
IDX = '/home/user/work/index'

def load(tag):
    return json.load(open(f'{IDX}/{tag}.json'))

def render_segs(path, segs, out, dpi=170, margin_x=20):
    doc = pymupdf.open('/home/user/' + path)
    ims = []
    for (p, y0, y1) in segs:
        page = doc[p]
        clip = pymupdf.Rect(margin_x, max(0, y0 - 2), page.rect.width - margin_x, min(page.rect.height, y1 + 2))
        pix = page.get_pixmap(clip=clip, dpi=dpi)
        ims.append(Image.frombytes('RGB', (pix.width, pix.height), pix.samples))
    W = max(i.width for i in ims); H = sum(i.height for i in ims)
    canvas = Image.new('RGB', (W, H), 'white'); y = 0
    for i in ims:
        canvas.paste(i, (0, y)); y += i.height
    canvas.save(out)
    return out

def main():
    mode, tag = sys.argv[1], sys.argv[2]
    outdir = '/home/user/work/renders'
    if mode == 'q':
        qno = int(sys.argv[3]); outdir = sys.argv[4] if len(sys.argv) > 4 else outdir
        dpi = int(sys.argv[5]) if len(sys.argv) > 5 else 170
        os.makedirs(outdir, exist_ok=True)
        for q in load(tag):
            if q['kind'] == 'q' and q['qno'] == qno:
                print(render_segs(q['file'], q['segs'], f'{outdir}/{tag}_q{qno}.png', dpi)); return
        print('not found')
    elif mode == 'm':
        mid = sys.argv[3]; outdir = sys.argv[4] if len(sys.argv) > 4 else outdir
        os.makedirs(outdir, exist_ok=True)
        for q in load(tag):
            if q['kind'] == 'material' and q['mid'] == mid:
                print(render_segs(q['file'], q['segs'], f'{outdir}/{mid}.png', 170)); return
        print('not found')
    elif mode == 'page':
        p = int(sys.argv[3]); outdir = sys.argv[4] if len(sys.argv) > 4 else outdir
        dpi = int(sys.argv[5]) if len(sys.argv) > 5 else 130
        os.makedirs(outdir, exist_ok=True)
        f = load(tag)[0]['file']
        doc = pymupdf.open('/home/user/' + f)
        pix = doc[p].get_pixmap(dpi=dpi); out = f'{outdir}/{tag}_p{p}.png'; pix.save(out); print(out)
    elif mode == 'ans':
        import json as _j
        a = _j.load(open(f'/home/user/work/answers/{tag}.json'))
        doc = pymupdf.open('/home/user/' + a['file'])
        t = unicodedata.normalize('NFKC', '\n'.join(pg.get_text() for pg in doc))
        for m in re.finditer(sys.argv[3], t):
            print('-----', m.start()); print(t[max(0, m.start() - 50): m.start() + 1200])
main()
