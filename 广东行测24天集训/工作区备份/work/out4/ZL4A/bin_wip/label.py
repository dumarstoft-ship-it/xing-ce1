"""label.py <tag> <q0> [<tag> <q0> ...]: show the text between the end of question q0-1 and the start of q0 (material header), first 160 chars,
plus the position of this material among the paper's 资料 materials (by counting 资料 blocks)."""
import json, sys, re, unicodedata, pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
W = '/home/user/work'
args = sys.argv[1:]
for i in range(0, len(args), 2):
    tag, q0 = args[i], int(args[i + 1])
    d = json.load(open(f'{W}/index/{tag}.json'))
    qs = {x['qno']: x for x in d if x['kind'] == 'q'}
    f = qs[q0]['file']; doc = pymupdf.open('/home/user/' + f)
    prev = qs.get(q0 - 1)
    ps, ys = (prev['segs'][-1][0], prev['segs'][-1][2]) if prev else (qs[q0]['segs'][0][0], 0)
    pe, ye = qs[q0]['segs'][0][0], qs[q0]['segs'][0][1]
    t = ''
    for p in range(ps, pe + 1):
        y0 = ys if p == ps else 0; y1 = ye if p == pe else doc[p].rect.height
        t += doc[p].get_text('text', clip=pymupdf.Rect(0, y0, doc[p].rect.width, y1))
    t = re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', t))
    # previous question tail (to catch material text appended to previous question's segment)
    tail = re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', prev['text']))[-160:] if prev else ''
    print(f'{tag} q{q0}: [{t[:220]}]')
    m = re.search(r'(\(材料\d?\)|\([一二三四五六]\)|[（(][一二三四五六][)）]|材料[一二三四五六\d])', tail)
    if m: print(f'    prev-tail has label: ...{tail[m.start():m.start()+80]}')
