"""ans.py TAG QNO [QNO..] : print analysis text segment for given question numbers (text-layer analyses only)."""
import json, pymupdf, re, sys, unicodedata
pymupdf.TOOLS.mupdf_display_errors(False)
tag = sys.argv[1]
a = json.load(open(f'/home/user/work/answers/{tag}.json'))
d = pymupdf.open('/home/user/' + a['file'])
pages = [unicodedata.normalize('NFKC', p.get_text()) for p in d]
full = ''; starts = []
for i, p in enumerate(pages):
    starts.append(len(full)); full += p + '\n'
def page_of(pos):
    k = 0
    for i, s in enumerate(starts):
        if s <= pos: k = i
    return k + 1
for q in map(int, sys.argv[2:]):
    pat = re.compile(r'(?m)^\s*(?:第\s*)?%d\s*(?:题|[、\.．:：]|\s*\n)|【\s*%d\s*】|^\s*%d\s*$' % (q, q, q))
    hits = [m.start() for m in pat.finditer(full)]
    best = None
    for h in hits:
        seg = full[h:h + 2500]
        if re.search(r'答案|故选|选择[A-D]|因此,选|正确答案', seg[:2500]): best = h; break
    if best is None and hits: best = hits[0]
    print(f'===== {tag} Q{q}  file={a["file"]}  page={page_of(best) if best is not None else None}  auto={a["answers"].get(str(q))}')
    if best is not None:
        seg = full[best:best + 1600]
        print(re.sub(r'\n+', ' ', seg))
