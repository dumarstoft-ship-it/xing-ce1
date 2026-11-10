import pymupdf, re, json, sys, unicodedata, bisect
pymupdf.TOOLS.mupdf_display_errors(False)
QMARK = re.compile(r'(?:^|\n)\s*(?:第\s*(\d{1,3})\s*题|【\s*(?:解析\s*)?(\d{1,3})\s*(?:[—\-－]|】)|题目\s*(\d{1,3})|(\d{1,3})\s*[、\.．](?!\d)|(\d{1,3})[ \t]*\n(?!\s*\d))')
ANS = re.compile(r'(?:正确答案(?:是|为)?|参考答案(?:是|为)?|【答案】|答案(?:是|为)?)\s*[:：]?\s*[【\[]?\s*([A-H])')
ANS2 = re.compile(r'(?:故(?:本题)?(?:正确答案|答案)?(?:为|选|是)|因此[,，]?\s*选择|答案锁定)\s*[:：]?\s*[【\[]?([A-H])')
_cache = {}
def load(path):
    if path in _cache: return _cache[path]
    doc = pymupdf.open('/home/user/' + path)
    texts = []; starts = []; pos = 0
    for p in doc:
        t = unicodedata.normalize('NFKC', p.get_text()); t = re.sub(r'[ \t]+', ' ', t)
        starts.append(pos); texts.append(t); pos += len(t) + 1
    full = '\n'.join(texts)
    marks = []
    for m in QMARK.finditer(full):
        n = int(next(g for g in m.groups() if g)); marks.append((m.start(), n))
    seq, last = [], 0
    for p_, n in marks:
        if last < n <= last + 3: seq.append((p_, n)); last = n
    _cache[path] = (full, starts, seq)
    return _cache[path]
def seg(path, N):
    full, starts, seq = load(path)
    for i, (p_, n) in enumerate(seq):
        if n == N:
            end = seq[i + 1][0] if i + 1 < len(seq) else len(full)
            s = full[p_:end]
            page = bisect.bisect_right(starts, p_)  # 1-based
            a = ANS.search(s) or ANS2.search(s)
            # final answer: last '故正确答案为X' style if exists
            fin = re.findall(r'(?:正确答案为|故选|答案为|选择)\s*([A-D])', s)
            return dict(page=page, ans=a.group(1) if a else None, final=fin[-1] if fin else None, text=s)
    return None
if __name__ == '__main__':
    path, N = sys.argv[1], int(sys.argv[2]); r = seg(path, N)
    if not r: print('NOTFOUND'); sys.exit()
    print('page', r['page'], 'ans', r['ans'], 'final', r['final']); print(r['text'][:int(sys.argv[3]) if len(sys.argv) > 3 else 1500])
