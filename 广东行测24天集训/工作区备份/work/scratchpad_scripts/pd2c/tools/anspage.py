import pymupdf, re, sys, json, unicodedata
pymupdf.TOOLS.mupdf_display_errors(False)
W = '/home/user/work'
def pages_of(path):
    d = pymupdf.open('/home/user/' + path)
    return [unicodedata.normalize('NFKC', p.get_text()) for p in d]
def find(tag, q):
    a = json.load(open(f'{W}/answers/{tag}.json'))
    f = a['file']; P = pages_of(f)
    pats = [rf'第\s*{q}\s*题', rf'【题目\s*{q}\s*】', rf'题目\s*{q}\s*解析', rf'(?:^|\n)\s*{q}\s*[\.、．]\s*(?:正确答案|解析|【|\n|答案)', rf'(?:^|\n)\s*{q}\s*[\.、．]']
    for pat in pats:
        hits = [(i + 1, m.start()) for i, t in enumerate(P) for m in re.finditer(pat, t)]
        if hits:
            i, pos = hits[0]
            ctx = P[i - 1][pos: pos + 160].replace('\n', ' ')
            ans = re.search(r'正确答案[^A-D]{0,12}([A-D])', P[i - 1][pos: pos + 4000])
            return f, i, pat, ctx, (ans.group(1) if ans else None)
    return f, None, None, None, None
for arg in sys.argv[1:]:
    tag, q = arg.rsplit(':', 1)
    f, page, pat, ctx, ans = find(tag, int(q))
    print(f'{tag}:{q} page={page} ans_in_text={ans} | {ctx}')
    print(f'      file={f}')
