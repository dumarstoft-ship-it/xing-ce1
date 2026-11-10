import json,re,collections
raw=open('/home/user/xing-ce1/学习资料/盖句精读（词句新版·全151篇·手机版）(2).html',encoding='utf-8').read()
m=re.search(r'<script id="data" type="application/json">(.*?)</script>',raw,re.S)
D=json.loads(m.group(1))
cl=[json.loads(l) for l in open('/home/user/work/out/claims.jsonl') if l.strip()]
used={c['key'].split(':')[1] for c in cl if c['key'].startswith('HTML:')}
def ptext(para): return ''.join(sg.get('t', sg.get('m', '')) for sg in para)
REF=re.compile(r'第\d+段|标题|全文|上一段|下一段|上段|下段|前一段|后一段|上文|下文|前文|后文|文章开头|文末|篇末|开篇')
rows=[]
for a in D:
    if a['id'] in used: continue
    paras=[ptext(p) for p in a['paras']]
    k=collections.Counter(q['kind'] for q in a['q'])
    flags=[]
    for q in a['q']:
        t=paras[q['p']-1]
        ans=[t[b['b']:b['e']] for b in q['blanks']]
        # answer echoed elsewhere in article
        full='\n'.join(paras)
        for x in ans:
            cnt=full.count(x)
            if cnt>1 and len(x)>=2: flags.append(f"{q['id']}:echo'{x}'x{cnt}")
        refs=set(REF.findall(q['note']))
        if refs: flags.append(f"{q['id']}:ref{sorted(refs)}")
        same=[o['id'] for o in a['q'] if o['p']==q['p'] and o['id']!=q['id']]
        if same: flags.append(f"{q['id']}:samepara{same}")
    rows.append((a['id'],a['src'][:2],a['col'],k['选词填空'],k['语句填空'],a.get('kind'),a['title'][:22],flags))
for r in sorted(rows,key=lambda r:(len(r[7]),r[0])):
    print(f"{r[0]:22s} {r[1]} {r[2][:6]:6s} X{r[3]}Y{r[4]} {r[5] or '':2s} {r[6]:22s} nflags={len(r[7])} {' '.join(r[7])[:300]}")
