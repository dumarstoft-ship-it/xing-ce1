import json, sys, os, pickle, collections, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pool2 import load_all, cluster
IDX='/home/user/work/index'
tags=[t[:-5] for t in os.listdir(IDX) if t.endswith('.json')]
prov=[t for t in tags if re.match(r'(ZJ|JS|SD|SC|HB|SZ)20', t)]
gk=[t for t in tags if re.match(r'GK20(1[7-9]|2[0-5])', t)]
rows=[r for r in load_all(sorted(prov+gk)) if r['type']=='PX']
cl=cluster(rows, 0.5)
out=[]
for c in cl:
    rep=sorted(c, key=lambda r:(r['tag'].endswith('_xc') and not r['pid'].startswith(('ZJ','JS','SD','SC','HB','SZ')), r['ans'] is None))[0]
    y=int(re.search(r'20\d\d', rep['pid']).group())
    out.append((rep['pid'][:2], y, rep['key'], rep['tag'], rep['ans'], any(r['taken'] for r in c), sorted({r['key'] for r in c}), rep['nb'][:60]))
pickle.dump(cl, open('px_clusters.pkl','wb'))
cnt=collections.Counter()
for o in sorted(out, key=lambda x:(x[0]!='GK', -x[1], x[2])):
    cnt[(o[0]=='GK', o[5])]+=1
    print(o[0], o[1], o[2], o[3], o[4], 'TAKEN' if o[5] else 'free', ','.join(k for k in o[6] if k!=o[2]), '|', o[7])
print(cnt)
