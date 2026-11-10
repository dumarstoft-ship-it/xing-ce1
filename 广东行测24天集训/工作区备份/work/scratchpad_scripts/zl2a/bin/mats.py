"""mats.py <tag>... : list 资料 materials in order with q ranges and existing zl_materials ids"""
import json, sys, os, unicodedata
W = '/home/user/work'
ex = {}
for m in os.listdir(f'{W}/out/zl_materials'):
    try:
        d = json.load(open(f'{W}/out/zl_materials/{m}/material.json'))
        ex[m] = d
    except Exception: pass
for tag in sys.argv[1:]:
    d = json.load(open(f'{W}/index/{tag}.json'))
    qs = [x for x in d if x['kind'] == 'q' and x.get('section') == '资料']
    mids = []
    for x in qs:
        if x.get('material') not in mids: mids.append(x.get('material'))
    print('##', tag, d[0]['file'])
    for i, mid in enumerate(mids, 1):
        nos = [x['qno'] for x in qs if x.get('material') == mid]
        m = next((y for y in d if y['kind'] == 'material' and y['mid'] == mid), None)
        lab = unicodedata.normalize('NFKC', m['text'][:40]).replace('\n', ' ') if m else ''
        segs = m['segs'] if m else None
        print(f'  #{i} {mid} q{nos[0]}-{nos[-1]} segs={segs} | {lab}')
    paper = tag.replace('_xc', '')
    print('  existing:', sorted(k for k in ex if k.startswith(f'ZLM-{paper}-') or k.startswith(f'ZLM-{tag}-')))
