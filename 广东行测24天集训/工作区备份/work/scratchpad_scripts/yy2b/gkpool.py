import json, sys, collections, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pool import pool
years = range(2017, 2026)
tags = []
for y in years:
    for v in ['F','D','X']:
        for suf in ['', '_xc']:
            tags.append(f'GK{y}{v}{suf}')
P = pool(tags)
PD_TYPES = {'ZZ','BT','XJ','XW','CJ','TD','??'}
groups = collections.OrderedDict()
for r in P:
    if r['type'] not in PD_TYPES and r['type'] != 'PX': continue
    g = r['dup'] or f"{r['tag']}-{r['qno']}"
    groups.setdefault(g, []).append(r)
json.dump({g: [{k: v for k, v in r.items()} for r in rs] for g, rs in groups.items()}, open('gk_groups.json', 'w'), ensure_ascii=False)
cnt = collections.Counter(); free = collections.Counter(); noans = collections.Counter()
for g, rs in groups.items():
    y = min(int(r['pid'][2:6]) for r in rs)
    t = 'PX' if rs[0]['type']=='PX' else 'PD'
    cnt[(y,t)] += 1
    if not any(r['taken'] for r in rs):
        free[(y,t)] += 1
        if not any(r['ans'] for r in rs): noans[(y,t)] += 1
for y in years:
    print(y, 'PD', cnt[(y,'PD')], 'free', free[(y,'PD')], 'noans', noans[(y,'PD')], '| PX', cnt[(y,'PX')], 'free', free[(y,'PX')], 'noans', noans[(y,'PX')])
print('total PD free', sum(v for (y,t),v in free.items() if t=='PD'), 'PX free', sum(v for (y,t),v in free.items() if t=='PX'))
