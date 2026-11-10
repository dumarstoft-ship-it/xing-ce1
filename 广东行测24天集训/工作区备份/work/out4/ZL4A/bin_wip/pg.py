"""pg.py <tag> <page0> [dpi] [y0 y1]: render a page (0-based) to r/<tag>_p<page>.png"""
import pymupdf, json, sys
pymupdf.TOOLS.mupdf_display_errors(False)
tag, p = sys.argv[1], int(sys.argv[2]); dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 80
d = json.load(open(f'/home/user/work/index/{tag}.json'))
doc = pymupdf.open('/home/user/' + d[0]['file'])
clip = None
if len(sys.argv) > 5:
    clip = pymupdf.Rect(0, float(sys.argv[4]), doc[p].rect.width, float(sys.argv[5]))
pix = doc[p].get_pixmap(dpi=dpi, clip=clip)
out = f'/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl4a/r/{tag}_p{p}.png'
pix.save(out); print(out, pix.width, pix.height)
