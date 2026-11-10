# -*- coding: utf-8 -*-
import json, re, collections
HTML_FILE = '/home/user/xing-ce1/学习资料/盖句精读（词句新版·全151篇·手机版）(2).html'
raw = open(HTML_FILE, encoding='utf-8').read()
D = json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', raw, re.S).group(1))
cl = [json.loads(l) for l in open('/home/user/work/out/claims.jsonl') if l.strip()]
used = {c['key'].split(':')[1] for c in cl if c['key'].startswith('HTML:')}
def ptext(para): return ''.join(sg.get('t', sg.get('m', '')) for sg in para)
pat = re.compile(r'第\d+[、，—-]?\d*段|上一段|下一段|前一段|后一段|末段|首段|尾段|标题|全文|上一节|下一节|第[一二三四五六]部分|小标题|提要|摘要')
rows = []
for a in D:
    if a['id'] in used or a['kind'] == 'cs' or a['src'] != '人民日报': continue
    kc = collections.Counter(q['kind'] for q in a['q'])
    dep = []
    for q in a['q']:
        hits = pat.findall(q['note'])
        plen = len(ptext(a['paras'][q['p']-1]))
        dep.append((q['id'], q['kind'][:2], 'p%d' % q['p'], plen, len(hits)))
    samepara = len(a['q']) - len({q['p'] for q in a['q']})
    rows.append((a['id'], a['col'], a['date'], a['title'], kc['选词填空'], kc['语句填空'], len(a['paras']), dep, samepara, a['gname']))
for r in rows:
    print(f"{r[0]} {r[1]} {r[2]} 《{r[3]}》 选{r[4]} 语{r[5]} paras{r[6]} samepara{r[8]} | " + ' '.join(f"{d[0]}{d[1][0]}:{d[2]}/{d[3]}c/x{d[4]}" for d in r[7]) + f" | {r[9][:18]}")
