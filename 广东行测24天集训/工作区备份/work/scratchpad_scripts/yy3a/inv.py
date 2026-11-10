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
papers=sys.argv[1].split(',')
for p in papers:
    d=json.load(open(f'/home/user/work/index/{p}.json'))
    for q in d:
        if q['kind']!='q': continue
        t=q['text'] or ''
        if not re.search(r'填入|填写|横线|划线|画线', t): continue
        key=f"{p.replace('_xc','')}-{q['qno']}"
        r=qi.get((p,q['qno']),{})
        g=r.get('dup_group')
        ks={key}|set(groups.get(g,[]))
        tk=sorted({o for k in ks for o in taken.get(k,[])})
        print(f"{key:14s} sec={q.get('section')} dup={sorted(ks-{key})} taken={tk}")
        print('    ', t[:260].replace('\n',' '))
