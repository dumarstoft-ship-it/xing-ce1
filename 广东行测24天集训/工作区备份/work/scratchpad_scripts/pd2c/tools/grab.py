import pymupdf, re, sys, unicodedata
pymupdf.TOOLS.mupdf_display_errors(False)
path, pat = sys.argv[1], sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 900
d = pymupdf.open(path)
pages = [unicodedata.normalize('NFKC', p.get_text()) for p in d]
for i, t in enumerate(pages):
    for m in re.finditer(pat, t):
        print(f'----- page {i+1} pos {m.start()}')
        print(t[m.start(): m.start() + n])
