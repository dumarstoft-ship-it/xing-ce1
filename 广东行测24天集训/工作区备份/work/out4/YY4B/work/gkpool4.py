import json, sys, collections, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pool2 import load_all, cluster
PD = {'ZZ','BT','XJ','XW','CJ','TD','??'}
out=[]
for y in range(2013, 2026):
    tags = [f'GK{y}{v}{s}' for v in ['F','D','X',''] for s in ['','_xc']]
    rows = load_all(tags)
    for c in cluster(rows):
        pdrows = [r for r in c if not r['pz'] and r['type'] in PD]
        pxrows = [r for r in c if r['type']=='PX']
        kind = 'PD' if pdrows else ('PX' if pxrows else None)
        if not kind: continue
        types = sorted({('PZ' if r['pz'] else r['type']) for r in c})
        rep = sorted(pdrows or pxrows, key=lambda r:(r['ans'] is None, r['tag'].endswith('_xc'), 'FDX'.find(r['pid'][-1]) if r['pid'][-1] in 'FDX' else 0))[0]
        out.append(dict(year=y, kind=kind, key=rep['key'], tag=rep['tag'], qno=rep['qno'], type=rep['type'], types=types, ans=rep['ans'], rate=rep['rate'], yicuo=rep['yicuo'],
                        anss=sorted({(r['key'], r['ans'] or '-') for r in c}), taken=sorted({r['taken'] for r in c if r['taken']}),
                        members=sorted({r['key'] for r in c}), prompt=rep['prompt'], nb=rep['nb'], text=rep['text']))
json.dump(out, open('gk_pool4.json','w'), ensure_ascii=False, indent=0)
cnt=collections.Counter()
for o in out:
    cnt[(o['year'], o['kind'], 'taken' if o['taken'] else 'free')]+=1
for y in range(2013,2026):
    print(y, 'PD free', cnt[(y,'PD','free')], 'taken', cnt[(y,'PD','taken')], '| PX free', cnt[(y,'PX','free')], 'taken', cnt[(y,'PX','taken')])
