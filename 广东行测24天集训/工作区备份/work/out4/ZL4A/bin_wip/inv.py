"""Inventory of 资料 materials in range: per paper block of questions (by material, or blocks of 5 when segmentation merged),
claim status (replicating claim.py check), 比重 keyword hits.
usage: inv.py [minfree] [tag-regex]"""
import json, os, re, sys, unicodedata, collections
W = '/home/user/work'
SP = '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl4a'
MINFREE = int(sys.argv[1]) if len(sys.argv) > 1 else 4
rx = re.compile(sys.argv[2]) if len(sys.argv) > 2 else None
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
    for kk in sorted(ks):
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
BZ = re.compile(r'(比重|占比|占.{0,14}(的|比例)|所占|份额|贡献率|拉动|构成|比例)')
blocks = []
for t in TAGS:
    if rx and not rx.search(t): continue
    d = json.load(open(f'{W}/index/{t}.json'))
    paper = t.replace('_xc', '')
    qs = [x for x in d if x['kind'] == 'q' and x.get('section') == '资料']
    if not qs: continue
    qs.sort(key=lambda x: x['qno'])
    q0 = qs[0]['qno']
    b = collections.OrderedDict()
    for x in qs:
        b.setdefault((x['qno'] - q0) // 5, []).append(x)
    for k, xs in b.items():
        rows = []
        for x in xs:
            key = f'{paper}-{x["qno"]}'
            st = status(key)
            txt = re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', x['text']))
            rows.append((x['qno'], st, txt, ans.get(key), x.get('material')))
        blocks.append(dict(tag=t, paper=paper, blk=k + 1, rows=rows))
json.dump(blocks, open(f'{SP}/inv/blocks.json', 'w'), ensure_ascii=False)
tot = 0
for o in blocks:
    free = [r for r in o['rows'] if r[1] is None]
    if len(free) < MINFREE: continue
    tot += 1
    g = sum(1 for r in free if BZ.search(r[2]))
    print(f"## {o['tag']} B{o['blk']} q{o['rows'][0][0]}-{o['rows'][-1][0]} free={len(free)}/{len(o['rows'])} bzQ={g} mat={o['rows'][0][4]}")
    for (qno, st, txt, a, mm) in o['rows']:
        mark = '*' if BZ.search(txt) else ' '
        s = re.sub(r'^\d+\s*[\.、．]\s*', '', txt)
        print(f"  {mark}{qno:>3} {'F' if st is None else 'X:' + st[:6]:<9} {a or '-'} {s[:120]}")
print('blocks with >=', MINFREE, 'free:', tot, file=sys.stderr)
