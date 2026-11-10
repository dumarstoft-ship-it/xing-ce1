import pymupdf, sys, os
pymupdf.TOOLS.mupdf_display_errors(False)
path, pno = sys.argv[1], int(sys.argv[2])
dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 150
out = sys.argv[4]
clip = None
if len(sys.argv) > 6:
    y0, y1 = float(sys.argv[5]), float(sys.argv[6])
doc = pymupdf.open('/home/user/' + path)
page = doc[pno - 1]
if len(sys.argv) > 6:
    clip = pymupdf.Rect(0, page.rect.height * y0, page.rect.width, page.rect.height * y1)
pix = page.get_pixmap(dpi=dpi, clip=clip)
pix.save(out); print(out, pix.width, pix.height, 'pages=', len(doc))
