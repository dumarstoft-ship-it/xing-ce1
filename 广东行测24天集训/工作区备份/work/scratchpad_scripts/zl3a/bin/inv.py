"""Inventory of 资料 materials in range: per material, list questions, claim status (replicating claim.py check), growth-rate keyword hits.
usage: inv.py [minfree] > out"""
import json, os, re, sys, unicodedata, collections
W = '/home/user/work'
MINFREE = int(sys.argv[1]) if len(sys.argv) > 1 else 4
qrows = [json.loads(l) for l in open(f'{W}/qindex.jsonl')]
grp = {}; members = collections.defaultdict(set); ans = {}
for r in qrows:
    k = f"{r['pid']}-{r['qno']}"
    if r.get('dup_group'):
        grp[k] = r['dup_group']; members[r['dup_group']].add(k)
    if r.get('answer'): ans.setdefault(k, r['answer'])
claims = [json.loads(l) for l in open(f'{W}/out/claims.jsonl') if l.strip()]
ck = {}
for c in claims:
    for kk in [c['key']] + c.get('dups', []):
        ck.setdefault(kk, c['owner'])
def status(key):
    ks = {key}
    if key in grp: ks |= members[grp[key]]
    for kk in ks:
        if kk in ck: return ck[kk]
    return None
TAGS = []
for f in sorted(os.listdir(f'{W}/index')):
    t = f[:-5]
    m = re.match(r'([A-Z]+)(20\d\d)', t)
    prov, yr = m.group(1), int(m.group(2))
    ok = False
    if prov == 'GD' and 2013 <= yr <= 2023: ok = True
    if prov == 'GDXD': ok = True
    if prov == 'GK' and 2013 <= yr <= 2026: ok = True
    if prov in ('HB', 'SC', 'SD', 'SZ') and 2017 <= yr <= 2026: ok = True
    if prov == 'JS' and 2015 <= yr <= 2026: ok = True
    if prov in ('ZJ', 'ZJXD') and 2015 <= yr <= 2026: ok = True
    if ok: TAGS.append(t)
KW = re.compile(r'(增速|增长率|增幅|增长最快|增长最慢|最快|最慢|快于|慢于|高于|低于|百分点|同比|环比|超过|增长了?\d|下降|回落|提高|加快|放缓|年均|翻番|倍)')
GR = re.compile(r'(增速|增长率|增幅|最快|最慢|快于|慢于|增长最|下降最|降幅|百分点|加快|放缓|回落)')
out = []
for t in TAGS:
    d = json.load(open(f'{W}/index/{t}.json'))
    paper = t.replace('_xc', '')
    qs = [x for x in d if x['kind'] == 'q' and x.get('section') == '资料']
    mats = {x['mid']: x for x in d if x['kind'] == 'material'}
    order = []
    for x in qs:
        if x.get('material') not in order: order.append(x.get('material'))
    for i, mid in enumerate(order, 1):
        qq = [x for x in qs if x.get('material') == mid]
        rows = []
        for x in qq:
            key = f'{paper}-{x["qno"]}'
            st = status(key)
            txt = unicodedata.normalize('NFKC', x['text']).replace('\n', ' ')
            txt = re.sub(r'\s+', ' ', txt)
            rows.append((x['qno'], st, txt, ans.get(key), len(GR.findall(txt))))
        free = [r for r in rows if r[1] is None]
        m = mats.get(mid)
        lab = unicodedata.normalize('NFKC', m['text'][:60]).replace('\n', ' ') if m else '(no material seg)'
        out.append(dict(tag=t, paper=paper, idx=i, mid=mid, lab=lab, n=len(rows), nfree=len(free), gr=sum(r[4] for r in free), rows=rows,
                        segs=m['segs'] if m else None, nimg=len(m['images']) if m else 0))
json.dump(out, open('/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl3a/inv/inv.json', 'w'), ensure_ascii=False)
for o in out:
    if o['nfree'] < MINFREE: continue
    print(f"## {o['tag']} #{o['idx']} {o['mid']} n={o['n']} free={o['nfree']} gr={o['gr']} img={o['nimg']} | {o['lab'][:50]}")
    for (qno, st, txt, a, g) in o['rows']:
        print(f"   {qno:>3} {'FREE' if st is None else 'X:'+st[:10]:<13} a={a} g={g} {txt[:110]}")
