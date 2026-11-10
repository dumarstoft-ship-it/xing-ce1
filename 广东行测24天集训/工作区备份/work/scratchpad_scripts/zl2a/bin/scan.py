"""Scan in-scope 资料 questions; flag growth-amount (增长量) stems; attach claim status.
Scope: GK2017-2025, GD2017-2023 (+GDXD2019/2020), 外省 2020-2026 (HB JS SC SD SZ ZJ).
Output: v/cands.json (list of dict) and prints a compact table."""
import json, re, os, sys, unicodedata, collections
W = '/home/user/work'
SP = '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl2a'
rows = [json.loads(l) for l in open(f'{W}/qindex.jsonl')]
claims = [json.loads(l) for l in open(f'{W}/out/claims.jsonl') if l.strip()]
taken = {}
for c in claims:
    for k in [c['key']] + c.get('dups', []):
        taken.setdefault(k, c['owner'])

def in_scope(pid):
    m = re.match(r'([A-Z]+)(\d{4})', pid)
    if not m: return False
    p, y = m.group(1), int(m.group(2))
    if p == 'GK': return 2017 <= y <= 2025
    if p in ('GD', 'GDXD'): return 2017 <= y <= 2023
    if p in ('HB', 'JS', 'SC', 'SD', 'SZ', 'ZJ'): return 2020 <= y <= 2026
    return False

GROW = re.compile(r'(增长量|增量|增加了?多少|增长了?多少|增长约?多少|增加约?多少|多增|增加最多|增长最多|增加最少|增长最少|减少了?多少|下降了?多少|减少最多|净增|增长额|绝对量|增加额|比上年增加|比上年多|较上年增加|较上年多|多出|增加值最|增加超过|增长超过|增加(?:了)?(?:约)?[\d.]+|增长(?:了)?(?:约)?[\d.]+万|增加的|增长的绝对|增减|变化量|变动量|增加量|增长数量|多(?:了)?多少|少(?:了)?多少)')
idx = {}
for fn in os.listdir(f'{W}/index'):
    tag = fn[:-5]
    idx[tag] = json.load(open(f'{W}/index/{fn}'))
out = []
seen_groups = set()
for r in rows:
    if r['section'] != '资料' or not in_scope(r['pid']): continue
    d = idx[r['tag']]
    q = next((x for x in d if x['kind'] == 'q' and x['qno'] == r['qno']), None)
    if not q: continue
    t = unicodedata.normalize('NFKC', q['text'])
    stem = re.sub(r'\s+', '', t)
    key = f"{r['pid']}-{r['qno']}"
    g = r.get('dup_group')
    dup_seen = g in seen_groups
    seen_groups.add(g)
    flag = bool(GROW.search(stem))
    out.append(dict(tag=r['tag'], pid=r['pid'], qno=r['qno'], key=key, mat=q.get('material'), dup=g,
                    dup_seen=dup_seen, grow=flag, taken=taken.get(key), ans=r.get('answer'), rate=r.get('rate'),
                    stem=stem[:260]))
json.dump(out, open(f'{SP}/v/cands.json', 'w'), ensure_ascii=False, indent=0)
if __name__ == '__main__':
    n = collections.Counter()
    for o in out:
        n['all'] += 1
        if not o['dup_seen']: n['uniq'] += 1
        if o['grow'] and not o['dup_seen']: n['grow_uniq'] += 1
        if o['grow'] and not o['dup_seen'] and not o['taken']: n['grow_free'] += 1
    print(n)
