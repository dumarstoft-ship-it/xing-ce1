# -*- coding: utf-8 -*-
"""Full article with all question blanks masked inline; no notes.  python3 full.py <id> [...]"""
import json, re, sys
HTML_FILE = '/home/user/xing-ce1/学习资料/盖句精读（词句新版·全151篇·手机版）(2).html'
raw = open(HTML_FILE, encoding='utf-8').read()
D = json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', raw, re.S).group(1))
ART = {a['id']: a for a in D}
def ptext(para): return ''.join(sg.get('t', sg.get('m', '')) for sg in para)
for aid in sys.argv[1:]:
    a = ART[aid]
    print('='*100)
    print(aid, a['src'], a['col'], a['date'], a['page'], a['author'], '|', a['title'])
    ans = {}
    for i, p in enumerate(a['paras'], 1):
        t = ptext(p); spans = []
        for q in a['q']:
            if q['p'] != i: continue
            for k, b in enumerate(q['blanks']):
                spans.append((b['b'], b['e'], f"〖{q['id']}{'abc'[k] if len(q['blanks'])>1 else ''}:{t[b['b']:b['e']]}〗"))
        spans.sort(key=lambda x: -x[0])
        for b, e, rep in spans: t = t[:b] + rep + t[e:]
        segs = [('m' if 'm' in sg else 't') for sg in p]
        labels = [sg.get('label') for sg in p if sg.get('label')]
        print(f'[{i}] {t}' + (f'   <<labels:{labels}>>' if labels else ''))
