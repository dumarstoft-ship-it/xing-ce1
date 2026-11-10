import json,re,sys
raw=open('/home/user/xing-ce1/学习资料/盖句精读（词句新版·全151篇·手机版）(2).html',encoding='utf-8').read()
m=re.search(r'<script id="data" type="application/json">(.*?)</script>',raw,re.S)
D=json.loads(m.group(1)); ART={a['id']:a for a in D}
def ptext(para): return ''.join(sg.get('t', sg.get('m', '')) for sg in para)
ctx = 1 if '--ctx' in sys.argv else 0
for aid in [x for x in sys.argv[1:] if not x.startswith('--')]:
    a=ART[aid]
    print('='*90); print(aid, a['src'], a['col'], a['date'], '《'+a['title']+'》', 'np=',len(a['paras']), 'kind=',a.get('kind'))
    marks={}
    for q in a['q']:
        for i,b in enumerate(q['blanks']):
            marks.setdefault(q['p'],[]).append((b['b'],b['e'],q['id']+('' if len(q['blanks'])==1 else f'.{i+1}')))
    want=set()
    for p in marks:
        for d in range(-ctx,ctx+1): want.add(p+d)
    for i,p in enumerate(a['paras'],1):
        if i not in want: continue
        t=ptext(p)
        for b,e,lab in sorted(marks.get(i,[]),key=lambda x:-x[0]):
            t=t[:b]+'【'+lab+':'+t[b:e]+'】'+t[e:]
        print(f'[{i}]{"*" if i in marks else " "} {t}')
    for q in a['q']:
        print(f"  {q['id']} {q['kind'][:2]} p{q['p']} ans={'ABCD'[q['answer']]} {q['options']}")
