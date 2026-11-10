import pymupdf, re, json, os, sys, unicodedata
pymupdf.TOOLS.mupdf_display_errors(False)
QMARK = re.compile(r'(?:^|\n)\s*(?:第\s*(\d{1,3})\s*题|【\s*(?:解析\s*)?(\d{1,3})\s*(?:[—\-－]|】)|题目\s*(\d{1,3})|(\d{1,3})\s*[、\.．](?!\d)|(\d{1,3})[ \t]*\n(?!\s*\d))')
def segs(path):
    doc = pymupdf.open(path)
    pages=[unicodedata.normalize('NFKC', p.get_text()) for p in doc]
    offs=[]; t=''
    for i,p in enumerate(pages): offs.append(len(t)); t+=p+'\n'
    t2 = t
    marks = []
    for m in QMARK.finditer(t2):
        n = int(next(g for g in m.groups() if g)); marks.append((m.start(), n))
    seq, last = [], 0
    for pos, n in marks:
        if last < n <= last + 3: seq.append((pos, n)); last = n
    res = {}
    import bisect
    for i, (pos, n) in enumerate(seq):
        end = seq[i + 1][0] if i + 1 < len(seq) else len(t2)
        pg = bisect.bisect_right(offs, pos)  # 1-based page
        res[n] = dict(text=re.sub(r'\s+',' ',t2[pos:end]), page=pg)
    return res
if __name__=='__main__':
    tag=sys.argv[1]; qs=[int(x) for x in sys.argv[2].split(',')]
    a=json.load(open(f'/home/user/work/answers/{tag}.json'))
    r=segs('/home/user/'+a['file'])
    L=int(sys.argv[3]) if len(sys.argv)>3 else 400
    for q in qs:
        s=r.get(q)
        print(f'## {tag}-{q} p{s["page"] if s else "?"}:', (s['text'][:L] if s else 'NONE'))
