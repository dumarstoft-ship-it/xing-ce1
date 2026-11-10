"""pt.py <tag> <q0> <q1>: compact text layer of material + questions (collapsed whitespace per line, junk removed)."""
import json, sys, re, unicodedata, pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
W = '/home/user/work'
tag, q0, q1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
d = json.load(open(f'{W}/index/{tag}.json'))
qs = {x['qno']: x for x in d if x['kind'] == 'q'}
f = qs[q0]['file']
prev = qs.get(q0 - 1)
if prev and prev['segs'][-1][0] <= qs[q0]['segs'][0][0]:
    p_start, y_start = prev['segs'][-1][0], prev['segs'][-1][2]
else:
    p_start, y_start = qs[q0]['segs'][0][0], 0
p_end = qs[q1]['segs'][-1][0]; y_end = qs[q1]['segs'][-1][2]
doc = pymupdf.open('/home/user/' + f)
print('### FILE', f, 'pages', p_start + 1, '-', p_end + 1)
JUNK = re.compile(r'(本试卷由粉笔|网友回忆版\)|获取试卷更新|淘宝|Seeyee|公众号|第\s*\d+\s*页|^\s*-\s*\d+\s*-\s*$)')
for p in range(p_start, p_end + 1):
    page = doc[p]
    y0 = y_start if p == p_start else 0
    y1 = y_end if p == p_end else page.rect.height
    t = page.get_text('text', clip=pymupdf.Rect(0, y0, page.rect.width, y1))
    t = unicodedata.normalize('NFKC', t)
    out = []
    for ln in t.split('\n'):
        ln = re.sub(r'\s+', ' ', ln).strip()
        if not ln or JUNK.search(ln): continue
        out.append(ln)
    # join short table-cell lines with ' | '
    buf = []; res = []
    for ln in out:
        if len(ln) <= 14 and not re.match(r'^[A-D][\.、．]', ln) and not re.match(r'^\d{2,3}[\.、．]', ln):
            buf.append(ln)
        else:
            if buf: res.append(' | '.join(buf)); buf = []
            res.append(ln)
    if buf: res.append(' | '.join(buf))
    print(f'--- p{p+1}')
    print('\n'.join(res))
