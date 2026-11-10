"""Survey data-analysis materials across all index files.
Material region for a block = from just after the previous question's option-D line to the start of the
block's first question (spanning pages). Block boundaries: index 'material' field when present, else
detected by long text in the gap. Reports chars/digits/images/drawings and claim status."""
import json, glob, os, re, sys, unicodedata
import pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
IDX = '/home/user/work/index'
SP = '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl4b'
claims = [json.loads(l) for l in open('/home/user/work/out/claims.jsonl') if l.strip()]
taken = {}
for c in claims:
    for k in [c['key']] + c.get('dups', []):
        taken.setdefault(k, c['owner'])

def lines_of(page):
    out = []
    for b in page.get_text('dict')['blocks']:
        if b.get('type') != 0: continue
        for l in b['lines']:
            t = ''.join(s['text'] for s in l['spans'])
            if t.strip():
                out.append((l['bbox'][1], l['bbox'][3], l['bbox'][0], t))
    out.sort()
    return out

def gap_region(doc, prev, first):
    """returns list of (page, y0, y1) for the gap between prev question's D-option line and first question start"""
    # end of prev options
    segs = prev['segs']
    yD = None; pD = None
    for (p, y0, y1) in segs:
        for (ly0, ly1, lx0, t) in lines_of(doc[p]):
            if ly0 >= y0 - 1 and ly1 <= y1 + 1:
                tt = unicodedata.normalize('NFKC', t).strip()
                if re.match(r'^D\s*([\.、．:：]|$)', tt) or re.search(r'\sD\s*[\.、．]', ' ' + tt):
                    yD, pD = ly1, p
    if yD is None:
        pD, yD = segs[0][0], segs[0][1]
    pF, yF = first['segs'][0][0], first['segs'][0][1]
    reg = []
    for p in range(pD, pF + 1):
        h = doc[p].rect.height
        a = yD if p == pD else 0
        b = yF if p == pF else h
        if b > a: reg.append((p, a, b))
    return reg

def region_text(doc, reg):
    out = []
    for (p, a, b) in reg:
        for (ly0, ly1, lx0, t) in lines_of(doc[p]):
            if ly0 >= a - 0.5 and ly1 <= b + 1:
                if re.search(r'本试卷由|粉笔用户|第\d+页，共\d+页|公务员录用考试《行测》题|^\s*-?\d+-?\s*$', t): continue
                out.append(t)
    return '\n'.join(out)

def region_stats(doc, reg):
    nimg = 0; ndraw = 0
    for (p, a, b) in reg:
        page = doc[p]
        W, H = page.rect.width, page.rect.height
        for info in page.get_image_info():
            bb = info['bbox']
            area = (bb[2] - bb[0]) * (bb[3] - bb[1])
            if area > 0.45 * W * H: continue  # page background / watermark
            if bb[3] > a and bb[1] < b and (bb[2] - bb[0]) > 60 and (bb[3] - bb[1]) > 30:
                nimg += 1
        for d in page.get_drawings():
            r = d['rect']
            if r.y1 > a and r.y0 < b:
                ndraw += 1
    return nimg, ndraw

def survey(tag):
    d = json.load(open(f'{IDX}/{tag}.json'))
    qs = sorted([x for x in d if x['kind'] == 'q'], key=lambda x: x['qno'])
    zl = [x for x in qs if x.get('section') == '资料']
    if not zl: return []
    pid = tag.replace('_xc', '')
    doc = pymupdf.open('/home/user/' + zl[0]['file'])
    byq = {x['qno']: x for x in qs}
    zlq = [x['qno'] for x in zl]
    # candidate boundaries: every question; keep those whose gap has long text
    rows = []
    gaps = {}
    for q in zlq:
        prev = byq.get(q - 1)
        if not prev: continue
        reg = gap_region(doc, prev, byq[q])
        txt = region_text(doc, reg)
        gaps[q] = (reg, txt)
    starts = []
    for q in zlq:
        if q == zlq[0]: starts.append(q); continue
        reg, txt = gaps.get(q, ([], ''))
        nimg, ndraw = region_stats(doc, reg)
        t = re.sub(r'\s+', '', txt)
        if len(t) > 150 or nimg > 0 or ndraw > 20 or re.search(r'(^|\n)\s*[（(][一二三四五六七八九][）)]|根据以下|材料[一二三四五六七八九\d]', txt):
            starts.append(q)
    for i, s in enumerate(starts):
        e = (starts[i + 1] - 1) if i + 1 < len(starts) else zlq[-1]
        reg, txt = gaps.get(s, ([], ''))
        nimg, ndraw = region_stats(doc, reg)
        t = re.sub(r'\s+', '', unicodedata.normalize('NFKC', txt))
        ndig = len(re.findall(r'\d', t))
        qnos = list(range(s, e + 1))
        st = [taken.get(f'{pid}-{q}', '') for q in qnos]
        rows.append(dict(tag=tag, pid=pid, start=s, end=e, n=len(qnos), chars=len(t), digits=ndig,
                         nimg=nimg, ndraw=ndraw, taken=st, text=txt, reg=reg,
                         page=(reg[0][0] + 1) if reg else None, file=zl[0]['file']))
    return rows

if __name__ == '__main__':
    tags = sys.argv[1:] or sorted(os.path.basename(f)[:-5] for f in glob.glob(f'{IDX}/*.json'))
    allrows = []
    for tag in tags:
        try:
            rows = survey(tag)
        except Exception as ex:
            print(tag, 'ERR', ex); continue
        allrows += rows
        for r in rows:
            free = sum(1 for t in r['taken'] if not t)
            head = re.sub(r'\s+', '', r['text'])[:60]
            print(f"{r['tag']:12s} {r['start']:3d}-{r['end']:3d} n={r['n']:2d} free={free:2d} ch={r['chars']:5d} dg={r['digits']:4d} img={r['nimg']:2d} drw={r['ndraw']:4d} p{r['page']} | {head}")
    json.dump(allrows, open(f'{SP}/survey.json', 'w'), ensure_ascii=False)
