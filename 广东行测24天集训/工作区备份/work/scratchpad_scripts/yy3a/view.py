import json,re,sys
raw=open('/home/user/xing-ce1/学习资料/盖句精读（词句新版·全151篇·手机版）(2).html',encoding='utf-8').read()
m=re.search(r'<script id="data" type="application/json">(.*?)</script>',raw,re.S)
D=json.loads(m.group(1)); ART={a['id']:a for a in D}
def ptext(para): return ''.join(sg.get('t', sg.get('m', '')) for sg in para)
shownote = '--note' in sys.argv
for aid in [x for x in sys.argv[1:] if not x.startswith('--')]:
    a=ART[aid]
    print('='*100); print(aid, a['src'], a['col'], a['date'], '《'+a['title']+'》', a['gname'], 'kind=',a.get('kind'))
    marks={}
    for q in a['q']:
        for i,b in enumerate(q['blanks']):
            marks.setdefault(q['p'],[]).append((b['b'],b['e'],q['id']+('' if len(q['blanks'])==1 else f'.{i+1}')))
    for i,p in enumerate(a['paras'],1):
        t=ptext(p)
        for b,e,lab in sorted(marks.get(i,[]),key=lambda x:-x[0]):
            t=t[:b]+'【'+lab+':'+t[b:e]+'】'+t[e:]
        print(f'[{i}] {t}')
    for q in a['q']:
        print(f"  {q['id']} {q['kind']} p{q['p']} ans={'ABCD'[q['answer']]} opts={q['options']}")
        if shownote: print('     note:', q['note'][:400])
