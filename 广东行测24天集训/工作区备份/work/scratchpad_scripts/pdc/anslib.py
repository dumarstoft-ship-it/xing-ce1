"""Locate the analysis segment (page + extracted answer) for a question in a text-layer analysis PDF."""
import json, pymupdf, re, unicodedata, functools
pymupdf.TOOLS.mupdf_display_errors(False)

@functools.lru_cache(None)
def load(tag):
    a = json.load(open(f'/home/user/work/answers/{tag}.json'))
    d = pymupdf.open('/home/user/' + a['file'])
    pages = [unicodedata.normalize('NFKC', p.get_text()) for p in d]
    full = ''; starts = []
    for p in pages:
        starts.append(len(full)); full += p + '\n'
    return a, full, starts

ANS = re.compile(r'(?:正确答案(?:是|为)?\s*[:：]?\s*【?\s*|故正确答案为|因此[,，]?\s*选择|故本题选|故选|答案为)\s*([A-D])')

def locate(tag, q):
    a, full, starts = load(tag)
    pats = [r'【\s*解析\s*%d\s*[—\-－]' % q, r'题目\s*%d\s*解析' % q, r'(?m)^\s*第\s*%d\s*题' % q, r'【\s*%d\s*】' % q, r'(?m)^\s*%d\s*[、\.．]\s*(?:解析|第一步)' % q,
            r'(?m)^\s*%d\s*\n\s*(?:\d+\s*\n)?\s*第一步' % q, r'(?m)^\s*%d\s*[、\.．]' % q]
    for p in pats:
        for m in re.finditer(p, full):
            seg = full[m.start(): m.start() + 3000]
            # stop at next question marker
            nxt = re.search(r'(?m)题目\s*%d\s*解析|【\s*解析\s*%d|^\s*第\s*%d\s*题|【\s*%d\s*】|^\s*%d\s*[、\.．]' % (q + 1, q + 1, q + 1, q + 1, q + 1), seg[5:])
            if nxt: seg = seg[: nxt.start() + 5]
            am = ANS.search(seg)
            if am:
                page = max(i for i, s in enumerate(starts) if s <= m.start()) + 1
                return dict(file=a['file'], page=page, ans=am.group(1), seg=seg)
    return dict(file=a['file'], page=None, ans=None, seg=None)

if __name__ == '__main__':
    import sys
    tag = sys.argv[1]
    for q in map(int, sys.argv[2:]):
        r = locate(tag, q)
        print(tag, q, 'page', r['page'], 'ans', r['ans'], '|', (r['seg'] or '')[:160].replace('\n', ' '))
