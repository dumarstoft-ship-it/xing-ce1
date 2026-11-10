import json, os, sys
W='/home/user/work'
QI=[json.loads(l) for l in open(f'{W}/qindex.jsonl')]
CL=[json.loads(l) for l in open(f'{W}/out/claims.jsonl') if l.strip()]
taken=set()
for c in CL:
    taken.add(c['key']); taken.update(c.get('dups',[]))
grp={}
for r in QI:
    grp.setdefault(r.get('dup_group'),[]).append(f"{r['pid']}-{r['qno']}")
key2grp={f"{r['pid']}-{r['qno']}":r.get('dup_group') for r in QI}
def is_free(key):
    ks={key}
    g=key2grp.get(key)
    if g: ks|=set(grp[g])
    return not (ks & taken), ks
def load(tag): return json.load(open(f'{W}/index/{tag}.json'))
def qkey(q): return f"{q['pid'].replace('_xc','')}-{q['qno']}"
