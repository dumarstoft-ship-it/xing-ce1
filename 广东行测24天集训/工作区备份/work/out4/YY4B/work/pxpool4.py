import json, sys, os, collections, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pool2 import load_all, cluster
IDX='/home/user/work/index'
tags=[t[:-5] for t in os.listdir(IDX) if t.endswith('.json')]
sel=[t for t in tags if re.match(r'(ZJ|ZJXD|JS|SD|SC|HB|SZ|GK|GDXD)20', t)]
rows=[r for r in load_all(sorted(sel)) if r['type']=='PX']
cl=cluster(rows, 0.5)
out=[]
for c in cl:
    rep=sorted(c, key=lambda r:(r['ans'] is None, r['tag'].endswith('_xc')))[0]
    y=int(re.search(r'20\d\d', rep['pid']).group())
    out.append(dict(prov=re.match(r'[A-Z]+',rep['pid']).group(0), year=y, key=rep['key'], tag=rep['tag'], qno=rep['qno'], ans=rep['ans'], rate=rep['rate'],
                    anss=sorted({(r['key'], r['ans'] or '-') for r in c}), taken=sorted({r['taken'] for r in c if r['taken']}), members=sorted({r['key'] for r in c}), nb=rep['nb'], text=rep['text']))
json.dump(out, open('px_pool4.json','w'), ensure_ascii=False, indent=0)
cnt=collections.Counter()
for o in sorted(out, key=lambda x:(x['prov']!='GK', x['prov'], -x['year'], x['key'])):
    cnt[(o['prov'], bool(o['taken']))]+=1
    if o['taken']: continue
    print(o['prov'], o['year'], o['key'], o['tag'], o['ans'], 'r=%s'%o['rate'], ','.join(k for k in o['members'] if k!=o['key']), '|', o['nb'][:60])
print(sorted(cnt.items()))
