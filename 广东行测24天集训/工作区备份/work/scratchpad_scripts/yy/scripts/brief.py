import json,sys
sys.path.insert(0,'/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/yy/scripts')
from hshow import A, ptext
def brief(aid, nlen=420, plen=400):
    a=A[aid]
    print('=== ', aid, a['src'], a['col'], a['date'], '《'+a['title']+'》', 'npara', len(a['paras']))
    for q in a['q']:
        p=q['p']; t=ptext(a['paras'][p-1])
        s=t
        for b in sorted(q['blanks'], key=lambda x:-x['b']): s=s[:b['b']]+'【____】'+s[b['e']:]
        print(f"  -- {q['id']} {q['kind']} p{p} ans={'ABCD'[q['answer']]}:{q['options'][q['answer']]} || opts: "+' | '.join(q['options']))
        print('     [p%d]'%p, s[:plen])
        print('     NOTE:', q['note'][:nlen])
if __name__=='__main__':
    for aid in sys.argv[1:]: brief(aid)
