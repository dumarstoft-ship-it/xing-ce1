"""pagetext.py <tag> <q0> <q1> : print the raw text layer of the pages spanning questions q0..q1 plus the preceding material pages
(from the page of the first question back to the page where the material starts: uses index material segs or previous question end)."""
import json, sys, re, unicodedata, pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
W = '/home/user/work'
tag, q0, q1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
d = json.load(open(f'{W}/index/{tag}.json'))
qs = {x['qno']: x for x in d if x['kind'] == 'q'}
f = qs[q0]['file']
prev = qs.get(q0 - 1)
p_start = prev['segs'][-1][0] if prev else qs[q0]['segs'][0][0]
y_start = prev['segs'][-1][2] if prev else 0
p_end = qs[q1]['segs'][-1][0]; y_end = qs[q1]['segs'][-1][2]
doc = pymupdf.open('/home/user/' + f)
print('FILE', f, 'pages', p_start + 1, '-', p_end + 1)
for p in range(p_start, p_end + 1):
    page = doc[p]
    y0 = y_start if p == p_start else 0
    y1 = y_end if p == p_end else page.rect.height
    t = page.get_text('text', clip=pymupdf.Rect(0, y0, page.rect.width, y1))
    t = unicodedata.normalize('NFKC', t)
    print(f'--- page {p+1} y{y0:.0f}-{y1:.0f}')
    print(t)
