"""Round-4 cleaning: text-layer extraction of passage / prompt / options. Every result is proofread against the page image afterwards."""
import re, sys, os, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qx import get, raw
import clean2
from clean2 import norm_text, j, PROMPT, CIRC
from clean3 import fix_radicals, RADICAL, EXTRA_JUNK
EXTRA4 = [r'20\d\d\s*国家公务员录用考试《行测》题[（(][^\n]*?[)）]', r'四、推理判断。[^\n]*(?:\n[^\n]*?1\s*项。)?', r'(?m)^\s*-\s*\d+\s*-\s*$',
          r'20\d\d年?[^\n]{0,12}公务员[^\n]{0,14}《行测》[^\n]*', r'20\d\d\s*年[^\n]{0,10}广东[^\n]{0,30}真题[^\n]*']
def dejunk4(t):
    t, ch = fix_radicals(t)
    for p in EXTRA_JUNK + EXTRA4: t = re.sub(p, '', t)
    return clean2.dejunk(t), ch
OPT = lambda L: re.compile(r'(?<![A-Za-z0-9])' + L + r'\s*[、\.．]\s*')
def find_opts4(t):
    pos = [list(OPT(L).finditer(t)) for L in 'ABCD']
    best = None
    for a in pos[0]:
        b = next((x for x in pos[1] if x.start() > a.start()), None)
        if not b: continue
        c = next((x for x in pos[2] if x.start() > b.start()), None)
        if not c: continue
        d = next((x for x in pos[3] if x.start() > c.start()), None)
        if not d: continue
        best = (a, b, c, d)
    return best
def clean_pd4(r):
    t, ch = dejunk4(r)
    t = re.sub(r'^\s*\d{1,3}\s*[、\.．]?\s*', '', t.strip())
    a, b, c, d = find_opts4(t)
    body = t[:a.start()]
    opts = {'A': j(t[a.end():b.start()]), 'B': j(t[b.end():c.start()]), 'C': j(t[c.end():d.start()]), 'D': j(t[d.end():])}
    lines = [l.strip() for l in body.strip().split('\n') if l.strip()]
    k = None
    for i in range(len(lines) - 1, -1, -1):
        if PROMPT.match(lines[i]): k = i; break
    if k is None: k = len(lines) - 1
    passage = ''.join(lines[:k]); prompt = ''.join(lines[k:])
    return norm_text(passage), norm_text(prompt), opts, ch
def clean_px4(r):
    t, ch = dejunk4(r)
    t = re.sub(r'^\s*\d{1,3}\s*[、\.．]?\s*(?=[①-⑧])', '', t.strip())
    t = re.sub(r'^\s*\d{1,3}\s*[、\.．]\s*', '', t)
    om = list(re.finditer(r'([A-D])\s*[\.．、]\s*([①-⑧](?:\s*[-－—]?\s*[①-⑧]){3,7})', t))
    opts = {m.group(1): re.sub(r'\s+', '', m.group(2)) for m in om}
    body = t[:om[0].start()]
    pm = re.search(r'((?:将以上|将上述|把以上)[^\n]*?(?:是|为)[^\n]*)', body)
    prompt = re.sub(r'\s+', '', pm.group(1)) if pm else ''
    lead = body[:body.find('①')]
    body2 = body.replace(pm.group(1), '') if pm else body
    chunks = [c for c in re.split(r'(?=[①-⑧])', body2) if c.strip() and c.strip()[0] in CIRC]
    sents = [norm_text(re.sub(r'\s+', '', c)) for c in chunks]
    return sents, norm_text(prompt), norm_text(re.sub(r'\s+', '', lead)), opts, ch
