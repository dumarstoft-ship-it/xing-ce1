"""print question text + analysis snippet for keys"""
import pool, sys, os, json, re, pymupdf, unicodedata
pymupdf.TOOLS.mupdf_display_errors(False)
def tag_of(pid):
    return pid if os.path.exists(f'/home/user/work/index/{pid}.json') else pid + '_xc'
_cache = {}
def ans_pages(tag):
    if tag in _cache: return _cache[tag]
    p = f'/home/user/work/answers/{tag}.json'
    if not os.path.exists(p): _cache[tag] = (None, []); return _cache[tag]
    a = json.load(open(p)); doc = pymupdf.open('/home/user/' + a['file'])
    pages = [unicodedata.normalize('NFKC', pg.get_text()) for pg in doc]
    _cache[tag] = (a['file'], pages); return _cache[tag]
def analysis(tag, q, width=1100):
    f, pages = ans_pages(tag)
    if f is None: return None, 'NO ANSWER FILE'
    if sum(len(p) for p in pages) < 2000: return f, 'SCANNED (no text layer), pages=%d' % len(pages)
    pats = [rf'(?:^|\n)\s*{q}\s*[\.、．]', rf'(?:^|\n)\s*【\s*{q}\s*】', rf'(?:^|\n)\s*第\s*{q}\s*题', rf'(?:^|\n)\s*{q}\s*\n', rf'题目\s*{q}\s*解析', rf'【解析\s*{q}\s*[—\-–]', rf'(?:^|\n)\s*{q}\s*[\.、．]?\s*【?(?:答案|解析)']
    out = []
    for i, t in enumerate(pages):
        for pt in pats:
            for m in re.finditer(pt, t):
                tt = t + (pages[i + 1] if i + 1 < len(pages) else '')
                out.append(f'[ans page {i+1}] ' + tt[m.start(): m.start() + width])
    return f, '\n....\n'.join(out[:3]) if out else 'NOT FOUND IN TEXT'
def show(key, width=1100):
    pid, q = key.rsplit('-', 1); q = int(q); tag = tag_of(pid)
    x = pool.qtext(tag, q); a = pool.answers(tag).get(str(q)) or {}
    print(f"=== {key} [{tag}] taken={pool.taken(key)} ans={a.get('ans')} rate={a.get('rate')} yicuo={a.get('yicuo')} page={x['segs'][0][0]+1 if x else None} file={x['file'] if x else None}")
    print(x['text'] if x else 'NOT FOUND')
    f, s = analysis(tag, q, width)
    print('--- ANALYSIS', f); print(s); print()
if __name__ == '__main__':
    w = 1100
    for k in sys.argv[1:]:
        if k.startswith('w='): w = int(k[2:]); continue
        show(k, w)
