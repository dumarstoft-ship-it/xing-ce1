import json, collections, re, os, sys
W = '/home/user/work'
rows = [json.loads(l) for l in open(f'{W}/qindex.jsonl')]
QI = {(r['pid'], r['qno']): r for r in rows}
grp = collections.defaultdict(set)
for r in rows:
    if r.get('dup_group'): grp[r['dup_group']].add(f"{r['pid']}-{r['qno']}")
def ks(key):
    pid, q = key.rsplit('-', 1); q = int(q)
    r = QI.get((pid, q)); s = {key}
    if r and r.get('dup_group'): s |= grp[r['dup_group']]
    return s
claims = [json.loads(l) for l in open(f'{W}/out/claims.jsonl') if l.strip()]
taken_keys = {}
for c in claims:
    for k in [c['key']] + c.get('dups', []):
        taken_keys.setdefault(k, c['owner'])
def taken(key):
    for k in ks(key):
        if k in taken_keys: return taken_keys[k]
    return None
IDX = {}
def idx(tag):
    if tag not in IDX:
        p = f'{W}/index/{tag}.json'
        IDX[tag] = json.load(open(p)) if os.path.exists(p) else []
    return IDX[tag]
def qtext(tag, qno):
    for q in idx(tag):
        if q.get('kind') == 'q' and q['qno'] == qno: return q
    return None
def answers(tag):
    p = f'{W}/answers/{tag}.json'
    return json.load(open(p))['answers'] if os.path.exists(p) else {}
