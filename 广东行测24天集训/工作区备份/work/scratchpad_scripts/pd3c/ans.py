import pymupdf, re, sys, unicodedata
pymupdf.TOOLS.mupdf_display_errors(False)
def find(path, qno, nxt=None, width=900, pat=None):
    doc = pymupdf.open('/home/user/' + path if not path.startswith('/') else path)
    pages = [unicodedata.normalize('NFKC', p.get_text()) for p in doc]
    pats = [pat] if pat else [rf'(?:^|\n)\s*【?\s*{qno}\s*[\.、．】]', rf'(?:^|\n)\s*第\s*{qno}\s*题', rf'(?:^|\n){qno}\s*\n']
    hits = []
    for i, t in enumerate(pages):
        for pt in pats:
            for m in re.finditer(pt, t):
                hits.append((i, m.start()))
    out = []
    for i, s in hits:
        t = pages[i] + (pages[i+1] if i + 1 < len(pages) else '')
        out.append((i + 1, t[s:s + width]))
    return out, len(pages)
if __name__ == '__main__':
    path, qno = sys.argv[1], int(sys.argv[2])
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 900
    res, n = find(path, qno, width=w)
    print('pages', n, 'hits', len(res))
    for pg, s in res[:4]:
        print('---- page', pg); print(s)
