import json, re, sys, collections, os, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classify import classify
IDX='/home/user/work/index'; ANS='/home/user/work/answers'
claims = [json.loads(l) for l in open('/home/user/work/out/claims.jsonl') if l.strip()]
taken = {}
for c in claims:
    for k in [c['key']] + c.get('dups', []):
        taken.setdefault(k.replace('_xc',''), c['owner'])
def norm(s):
    s = unicodedata.normalize('NFKC', s)
    s = re.sub(r'\d{4}\s*(国家|年).{0,30}(行测|副省|地市|行政执法)[^\n]*', '', s)
    s = re.sub(r'[\s　]', '', s)
    s = re.sub(r'^\d{1,3}[\.、．]?(\(单选题\))?', '', s)
    s = re.sub(r'[_＿\-—–]{2,}|\(\s*\)|（\s*）', '', s)
    s = re.sub(r'[^一-鿿0-9A-Za-z%]', '', s)
    return s
def split_body(t):
    m = re.search(r'\n\s*A\s*[\.、．]', t)
    body = t[:m.start()] if m else t
    opts = t[m.start():] if m else ''
    return body, opts
def grams(s, n=4): return {s[i:i+n] for i in range(max(0, len(s)-n+1))}
def ans_of(tag, qno):
    p = f'{ANS}/{tag}.json'
    if not os.path.exists(p): return {}
    return json.load(open(p))['answers'].get(str(qno)) or {}
def load_all(tags):
    out = []
    for tag in tags:
        if not os.path.exists(f'{IDX}/{tag}.json'): continue
        ix = json.load(open(f'{IDX}/{tag}.json'))
        mats = [m for m in ix if m['kind']=='material' and m.get('section')=='言语' and m.get('segs')]
        mstart = min(((m['segs'][0][0], m['segs'][0][1]) for m in mats), default=None)
        for q in ix:
            if q['kind']!='q' or q.get('section')!='言语': continue
            k, p = classify(q['text'])
            body, opts = split_body(q['text'])
            nb = norm(body.replace(p, '')) if p else norm(body)
            pos = (q['segs'][0][0], q['segs'][0][1]) if q.get('segs') else (0,0)
            pz = bool(mstart and pos > mstart) or (len(nb) < 60 and k not in ('PX',))
            pid = tag.replace('_xc','')
            a = ans_of(tag, q['qno'])
            out.append(dict(tag=tag, pid=pid, qno=q['qno'], key=f"{pid}-{q['qno']}", type=k, pz=pz, prompt=p, nb=nb, g=grams(nb),
                            ans=a.get('ans'), rate=a.get('rate'), yicuo=a.get('yicuo'), taken=taken.get(f"{pid}-{q['qno']}"), text=q['text'], file=q['file'], segs=q['segs']))
    return out
def cluster(rows, thr=0.55):
    # union-find on containment similarity
    par = list(range(len(rows)))
    def f(i):
        while par[i]!=i: par[i]=par[par[i]]; i=par[i]
        return i
    for i in range(len(rows)):
        for j in range(i+1, len(rows)):
            a, b = rows[i]['g'], rows[j]['g']
            if len(a) < 40 or len(b) < 40: continue
            inter = len(a & b)
            if inter >= 25 and inter / min(len(a), len(b)) >= thr:
                par[f(i)] = f(j)
    cl = collections.defaultdict(list)
    for i, r in enumerate(rows): cl[f(i)].append(r)
    return list(cl.values())
