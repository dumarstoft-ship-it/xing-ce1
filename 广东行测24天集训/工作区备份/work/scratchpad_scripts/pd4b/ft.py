# full-text search across index (all sections), print key, taken, section, prompt tail. No answers.
import json,os,re,sys,collections
W='/home/user/work'
pat=re.compile(sys.argv[1])
qi=[json.loads(l) for l in open(f'{W}/qindex.jsonl')]
sec={(r['pid'],r['qno']):r for r in qi}
claims=[json.loads(l) for l in open(f'{W}/out/claims.jsonl') if l.strip()]
taken={}
for c in claims:
    for k in [c['key']]+c.get('dups',[]): taken.setdefault(k,c['owner'])
grp=collections.defaultdict(list)
for r in qi:
    if r.get('dup_group'): grp[r['dup_group']].append(f"{r['pid']}-{r['qno']}")
def tk(k,g):
    ks=set(grp[g]) if g else set(); ks.add(k)
    for x in ks:
        if x in taken: return taken[x]
    return None
seen=set()
only_free='--free' in sys.argv
for fn in sorted(os.listdir(f'{W}/index')):
    tag=fn[:-5]
    for q in json.load(open(f'{W}/index/{fn}')):
        if q.get('kind')!='q': continue
        pid=q['pid'].replace('_xc','')
        k=f"{pid}-{q['qno']}"
        if k in seen: continue
        t=re.sub(r'\s','',q['text'])
        m=re.search(r'A[\.．、]',t)
        pre=t[:m.start()] if m else t
        mm=pat.search(pre)
        if not mm: continue
        seen.add(k)
        r=sec.get((pid,q['qno']),{})
        T=tk(k,r.get('dup_group'))
        if only_free and T: continue
        seg=[s for s in re.split(r'[。！？]',pre) if s.strip()]
        print(k, r.get('section'), 'TAKEN:'+T if T else 'FREE', 'n=%d'%len(pre), 'rate=%s'%r.get('rate'), '|', (seg[-1] if seg else '')[-45:])
