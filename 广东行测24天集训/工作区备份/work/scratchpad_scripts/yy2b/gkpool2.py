import json, sys, collections, os, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pool2 import load_all, cluster
years = range(2017, 2026)
allrows = []
for y in years:
    tags = [f'GK{y}{v}{s}' for v in ['F','D','X',''] for s in ['','_xc']]
    rows = load_all(tags)
    for c in cluster(rows):
        cid = f"C{y}-{len(allrows):04d}"
        allrows.append(c)
pickle.dump(allrows, open('gk_clusters.pkl','wb'))
PD = {'ZZ','BT','XJ','XW','CJ','TD','??'}
stat = collections.Counter(); free = collections.Counter(); noans=collections.Counter(); mixed=[]
for c in allrows:
    y = min(int(r['pid'][2:6]) for r in c)
    types = {('PZ' if r['pz'] else r['type']) for r in c}
    pdrows = [r for r in c if not r['pz'] and r['type'] in PD]
    pxrows = [r for r in c if r['type']=='PX']
    if pdrows:
        stat[(y,'PD')] += 1
        if not any(r['taken'] for r in c):
            free[(y,'PD')] += 1
            if not any(r['ans'] for r in pdrows): noans[(y,'PD')] += 1
    if pxrows:
        stat[(y,'PX')] += 1
        if not any(r['taken'] for r in c):
            free[(y,'PX')] += 1
            if not any(r['ans'] for r in pxrows): noans[(y,'PX')] += 1
    if len(types) > 1 and (pdrows or pxrows): mixed.append(c)
for y in years:
    print(y, 'PD', stat[(y,'PD')], 'free', free[(y,'PD')], 'noans', noans[(y,'PD')], '| PX', stat[(y,'PX')], 'free', free[(y,'PX')], 'noans', noans[(y,'PX')])
print('PD free total', sum(v for k,v in free.items() if k[1]=='PD'), 'PX free total', sum(v for k,v in free.items() if k[1]=='PX'))
print('mixed-type clusters (same passage, different question types):', len(mixed))
for c in mixed[:40]:
    print('  ', [(r['key'], 'PZ' if r['pz'] else r['type']) for r in c])
