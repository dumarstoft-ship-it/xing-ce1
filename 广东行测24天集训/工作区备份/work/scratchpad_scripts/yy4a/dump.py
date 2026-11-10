# -*- coding: utf-8 -*-
"""Dump HTML articles for editorial reading.  python3 dump.py <mode> <article id> [...]
mode q    : each question = its paragraph with the blank masked (other questions' blanks of the same paragraph shown as 〖qN〗), options, answer, note
mode full : whole article, every question blank masked as 〖qN:____〗, then the question list
"""
import json, re, sys
HTML_FILE = '/home/user/xing-ce1/学习资料/盖句精读（词句新版·全151篇·手机版）(2).html'
raw = open(HTML_FILE, encoding='utf-8').read()
D = json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', raw, re.S).group(1))
ART = {a['id']: a for a in D}
def ptext(para): return ''.join(sg.get('t', sg.get('m', '')) for sg in para)
def masked(a, pno, target=None, show=True):
    t = ptext(a['paras'][pno-1]); spans=[]
    for q in a['q']:
        if q['p'] != pno: continue
        for b in q['blanks']:
            if target is not None and q['id'] == target: spans.append((b['b'], b['e'], '【____】'))
            else: spans.append((b['b'], b['e'], f"〖{q['id']}另题〗"))
    spans.sort(key=lambda x:-x[0])
    for b,e,rep in spans: t = t[:b]+rep+t[e:]
    return t
mode = sys.argv[1]
for aid in sys.argv[2:]:
    a = ART[aid]
    print('='*100)
    print(aid, a['src'], a['col'], a['date'], a['page'], a['author'], '|', a['title'], '| kind', repr(a['kind']), '|', a['gname'])
    print('paras', len(a['paras']), 'chars', sum(len(ptext(p)) for p in a['paras']), '| q', [(q['id'], q['kind'][:2], 'p%d'%q['p'], len(q['blanks'])) for q in a['q']])
    if mode == 'full':
        for i in range(1, len(a['paras'])+1):
            print(f'[{i}] ' + masked(a, i))
        print('-'*60)
    for q in a['q']:
        t = ptext(a['paras'][q['p']-1])
        fills = [t[b['b']:b['e']] for b in q['blanks']]
        ok = ' '.join(fills) == q['options'][q['answer']]
        print(f"--- {q['id']} [{q['kind']}] p{q['p']} len(para)={len(t)} blanks={len(q['blanks'])} integrity={'OK' if ok else 'MISMATCH'}")
        if mode == 'q':
            print('   ' + masked(a, q['p'], q['id']))
        for k, o in zip('ABCD', q['options']):
            print(f"   {k}. {o}" + ('   ←' if 'ABCD'.index(k) == q['answer'] else ''))
        print('   NOTE: ' + q['note'])
