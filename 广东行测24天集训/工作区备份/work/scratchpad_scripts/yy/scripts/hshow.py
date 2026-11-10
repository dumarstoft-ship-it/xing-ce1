import json, sys, re
D=json.load(open('/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/yy/html_data.json'))
A={a['id']:a for a in D}
def ptext(para): return ''.join(sg.get('t', sg.get('m','')) for sg in para)
def show(aid, full_note=False, ctx=1):
    a=A[aid]
    print('=== ', aid, a['src'], a['col'], a['date'], a['page'], '《'+a['title']+'》', a['author'], '| group:', a['gname'], '| npara', len(a['paras']))
    for q in a['q']:
        p=q['p']; para=a['paras'][p-1]; t=ptext(para)
        # mask blanks
        s=t; 
        for b in sorted(q['blanks'], key=lambda x:-x['b']):
            s=s[:b['b']]+'【____】'+s[b['e']:]
        print(f"  -- {q['id']} {q['kind']} p{p} blanks={len(q['blanks'])} ans={'ABCD'[q['answer']]}:{q['options'][q['answer']]}")
        print('     opts:', ' | '.join(f"{'ABCD'[i]}.{o}" for i,o in enumerate(q['options'])))
        if ctx:
            if p>=2: print('     [prev p%d]'%(p-1), ptext(a['paras'][p-2])[:160])
        print('     [p%d]'%p, s)
        if ctx:
            if p<len(a['paras']): print('     [next p%d]'%(p+1), ptext(a['paras'][p])[:160])
        n=q['note']
        print('     NOTE:', n if full_note else n[:260])
if __name__=='__main__':
    for aid in sys.argv[1:]:
        show(aid, full_note=True)
