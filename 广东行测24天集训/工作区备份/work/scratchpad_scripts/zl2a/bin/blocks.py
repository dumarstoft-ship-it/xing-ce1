"""blocks.py <tag> <page0> [regex] : print text blocks (y0,y1,text) on a 0-based page of the tag's question PDF"""
import sys, json, re, unicodedata, pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
tag, p = sys.argv[1], int(sys.argv[2]); rx = re.compile(sys.argv[3]) if len(sys.argv) > 3 else None
f = json.load(open(f'/home/user/work/index/{tag}.json'))[0]['file']
pg = pymupdf.open('/home/user/' + f)[p]
for b in pg.get_text('blocks'):
    t = unicodedata.normalize('NFKC', b[4]).replace('\n', ' ')[:70]
    if rx is None or rx.search(t):
        print(f'{b[1]:7.1f} {b[3]:7.1f} | {t}')
for im in pg.get_image_info():
    r = im['bbox']; print(f'  IMG {r[1]:7.1f} {r[3]:7.1f} x{r[0]:.0f}-{r[2]:.0f}')
