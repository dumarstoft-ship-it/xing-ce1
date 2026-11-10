import json, re, sys
cl=[json.loads(l) for l in open('/home/user/work/out/claims.jsonl') if l.strip()]
taken={}
for c in cl:
    for k in [c['key']]+c.get('dups',[]):
        taken.setdefault(k,[]).append(c['owner'])
qi={}
groups={}
for l in open('/home/user/work/qindex.jsonl'):
    r=json.loads(l); qi[(r['pid'],r['qno'])]=r
    if r.get('dup_group'): groups.setdefault(r['dup_group'],[]).append(f"{r['pid']}-{r['qno']}")
p=sys.argv[1]; lo,hi=int(sys.argv[2]),int(sys.argv[3])
d=json.load(open(f'/home/user/work/index/{p}.json'))
for q in d:
    if q['kind']!='q' or not (lo<=q['qno']<=hi): continue
    t=q['text'] or ''
    key=f"{p.replace('_xc','')}-{q['qno']}"
    r=qi.get((p,q['qno']),{})
    g=r.get('dup_group')
    ks={key}|set(groups.get(g,[]))
    tk=sorted({o for k in ks for o in taken.get(k,[])})
    print(f"{key:14s} {q.get('section')} dup={sorted(ks-{key})} TAKEN={tk}")
    print('    ', t[:200].replace('\n',' '))
