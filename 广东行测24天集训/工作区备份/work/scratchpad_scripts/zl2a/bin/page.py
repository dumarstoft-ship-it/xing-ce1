"""page.py <pdf path (abs or rel to /home/user)> <page 1-based> [dpi] [y0 y1 in pt] -> PNG in r/"""
import sys, os, pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
p = sys.argv[1]; p = p if p.startswith('/') else '/home/user/' + p
n = int(sys.argv[2]); dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 110
doc = pymupdf.open(p); pg = doc[n - 1]
clip = None
if len(sys.argv) > 5:
    clip = pymupdf.Rect(0, float(sys.argv[4]), pg.rect.width, float(sys.argv[5]))
pix = pg.get_pixmap(dpi=dpi, clip=clip)
out = f'/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl2a/r/pg_{os.path.basename(p)[:12]}_{n}_{sys.argv[4] if clip else "f"}.png'
pix.save(out); print(out, doc.page_count, pg.rect)
