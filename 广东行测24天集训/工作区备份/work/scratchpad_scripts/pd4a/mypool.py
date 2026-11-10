"""compact pool with real claim status (incl. notsame overrides)"""
import json, glob, re, collections, sys, os
W='/home/user/work'
sys.path.insert(0,'/home/user/work/out3/PD3A/tools')
claims=[json.loads(l) for l in open(f'{W}/out/claims.jsonl') if l.strip()]
NS=[json.loads(l) for l in open(f'{W}/out/claims_notsame.jsonl') if l.strip()]
rows=[json.loads(l) for l in open(f'{W}/qindex.jsonl')]
bygrp=collections.defaultdict(set); grp={}
for r in rows:
    k=f"{r['pid']}-{r['qno']}"
    grp[k]=r.get('dup_group')
    if r.get('dup_group'): bygrp[r['dup_group']].add(k)
def dup_keys(key):
    ks={key}
    g=grp.get(key)
    if g: ks|=bygrp[g]
    for x in NS:
        if x['a']==key: ks.discard(x['b'])
        elif x['b']==key: ks.discard(x['a'])
    return ks
def status(key):
    ks=dup_keys(key)
    hit=[c for c in claims if c['key'] in ks or ks & set(c.get('dups',[]))]
    if not hit: return 'FREE',''
    d=[c for c in hit if c['key']==key]
    if d: return 'USED',d[0]['owner']
    return 'LOCK',hit[0]['owner']+'<'+hit[0]['key']
if __name__=='__main__':
    import pool
    P=pool.pool()
    flt=sys.argv[1] if len(sys.argv)>1 else ''
    for p in P:
        if flt and not re.search(flt,p['tag']): continue
        st,who=status(f"{p['pid']}-{p['qno']}")
        print(f"{p['tag']:11s}{p['qno']:4d} {'S' if p['space'] else 'P'} {str(p['ans'] or '-'):3s} {str(p['rate'] or '-'):5s} {st:4s} {who[:22]:22s} {p['stem'][:44]}")
