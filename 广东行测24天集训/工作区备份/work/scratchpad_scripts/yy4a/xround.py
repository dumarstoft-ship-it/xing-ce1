# -*- coding: utf-8 -*-
"""Cross-round repeat check (pre-selection): my candidate answers vs every answer used in D01-D09 (YY-A, YY2A, YY3A),
equal or one a substring of the other (len>=2). Also: my answers found inside earlier-round STEMS (seen before), info only."""
import json, re, sys
HTML_FILE = '/home/user/xing-ce1/学习资料/盖句精读（词句新版·全151篇·手机版）(2).html'
raw = open(HTML_FILE, encoding='utf-8').read()
D = json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', raw, re.S).group(1))
ART = {a['id']: a for a in D}
def ptext(para): return ''.join(sg.get('t', sg.get('m', '')) for sg in para)
prev = []   # (fill, where)
prev_q = []
for p, tag in [('out/YY-A/questions.jsonl','R1'),('out2/YY2A/questions.jsonl','R2'),('out3/YY3A/questions.jsonl','R3')]:
    for l in open('/home/user/work/'+p):
        if not l.strip(): continue
        q = json.loads(l)
        prev_q.append((tag, q))
        if q.get('answer_text'):
            fills = q['answer_text']
        else:
            opt = q['options'][q['checked_answer']]
            fills = opt.split(' ') if q['topic'] == '选词填空' else [opt]
            if q['source']['paper'].startswith('HTML'):
                a = ART[q['source']['article_id']]
                qq = [x for x in a['q'] if x['id'] == q['source']['qno'].split(':')[1]][0]
                t = ptext(a['paras'][qq['p']-1]); fills = [t[b['b']:b['e']] for b in qq['blanks']]
        for f in fills:
            prev.append((f, f"{tag} {q.get('official_day') or q['day']} {q['id']} {q['source']['paper']}-{q['source']['qno']}"))
print('previous answers:', len(prev), 'questions', len(prev_q))
mine = json.load(open(sys.argv[1]))   # {label: [fills]}
n = 0
for lab, fills in mine.items():
    for f in fills:
        if len(f) < 2: continue
        for pf, where in prev:
            if len(pf) < 2: continue
            if f == pf or f in pf or pf in f:
                n += 1; print(f'[repeat] {lab} “{f}” ~ “{pf}” ({where})')
print('repeats:', n)
m = 0
for lab, fills in mine.items():
    for f in fills:
        if len(f) < 3: continue
        for tag, q in prev_q:
            if f in q['stem']:
                m += 1; print(f'[seen in earlier-round stem] {lab} “{f}” in {tag} {q.get("official_day") or q["day"]} {q["id"]}')
print('seen-in-stem:', m)
