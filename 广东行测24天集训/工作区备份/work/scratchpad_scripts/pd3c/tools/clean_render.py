"""Render a question region at high dpi; blank out page header/footer text blocks (page numbers, ads) and collapse long blank bands."""
import sys, json, re, pymupdf
from PIL import Image, ImageDraw
import numpy as np
pymupdf.TOOLS.mupdf_display_errors(False)
IDX = '/home/user/work/index'
FOOT = re.compile(r'第\s*\d+\s*页\s*共\s*\d+\s*页|^\s*-\s*\d+\s*-\s*$|获取试卷更新|gwyeasy|公务员录用考试《行测》真题A$|^\s*\d+\s*/\s*\d+\s*$')
def render(tag, qno, out, dpi=200, gap=30):
    q = next(x for x in json.load(open(f'{IDX}/{tag}.json')) if x.get('kind') == 'q' and x['qno'] == qno)
    doc = pymupdf.open('/home/user/' + q['file'])
    ims = []
    for (p, y0, y1) in q['segs']:
        page = doc[p]
        clip = pymupdf.Rect(18, max(0, y0 - 2), page.rect.width - 18, min(page.rect.height, y1 + 2))
        pix = page.get_pixmap(clip=clip, dpi=dpi)
        im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        dr = ImageDraw.Draw(im); s = dpi / 72
        for b in page.get_text('blocks'):
            x0, by0, x1, by1, txt = b[0], b[1], b[2], b[3], b[4]
            if FOOT.search(txt.strip()) and by1 > clip.y0 and by0 < clip.y1:
                dr.rectangle([(x0 - clip.x0 - 2) * s, (by0 - clip.y0 - 2) * s, (x1 - clip.x0 + 2) * s, (by1 - clip.y0 + 2) * s], fill='white')
        ims.append(im)
    W = max(i.width for i in ims); canvas = Image.new('RGB', (W, sum(i.height for i in ims)), 'white'); y = 0
    for i in ims: canvas.paste(i, (0, y)); y += i.height
    arr = np.asarray(canvas.convert('L')); blank = (arr > 245).all(axis=1)
    keep = []; run = 0
    for r, bl in enumerate(blank):
        run = run + 1 if bl else 0
        if not bl or run <= gap: keep.append(r)
    out_im = Image.fromarray(np.asarray(canvas)[keep])
    a2 = np.asarray(out_im.convert('L')); rows = np.where((a2 <= 245).any(axis=1))[0]; cols = np.where((a2 <= 245).any(axis=0))[0]
    out_im = out_im.crop((max(0, cols[0] - 12), max(0, rows[0] - 12), min(out_im.width, cols[-1] + 12), min(out_im.height, rows[-1] + 12)))
    out_im.save(out); return out
if __name__ == '__main__':
    tag, qno, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    print(render(tag, qno, out))
