import pymupdf, sys
pymupdf.TOOLS.mupdf_display_errors(False)
path, pno, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
y0 = float(sys.argv[4]) if len(sys.argv)>4 else None
y1 = float(sys.argv[5]) if len(sys.argv)>5 else None
doc = pymupdf.open(path)
page = doc[pno]
r = page.rect
clip = pymupdf.Rect(0, y0 if y0 is not None else 0, r.width, y1 if y1 is not None else r.height)
pix = page.get_pixmap(clip=clip, dpi=110)
pix.save(out); print(out, r, len(doc))
