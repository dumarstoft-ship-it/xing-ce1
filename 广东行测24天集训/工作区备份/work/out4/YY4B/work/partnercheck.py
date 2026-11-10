import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simcheck import sims
from ansx import seg
def ans(tag,n):
    r=None
    try: r=seg(tag,n)
    except Exception as e: return ('ERR',None)
    if not r: 
        p=f'/home/user/work/answers/{tag}.json'
        a=json.load(open(p))['answers'].get(str(n),{}).get('ans') if os.path.exists(p) else None
        return ('auto-only',a)
    return (r['page'], r['ans'])
for k in sys.argv[1:]:
    tag,n=k.rsplit('-',1); n=int(n)
    me=ans(tag,n)
    ps=[(t,q) for c,t,q,sec,_ in (sims(tag,n) or []) if c>=0.9]
    out=[]
    for t,q in ps:
        if not os.path.exists(f'/home/user/work/answers/{t}.json'): out.append(f'{t}-{q}:no-ans-file'); continue
        out.append(f'{t}-{q}:{ans(t,q)}')
    print(k, me, '|', '; '.join(out))
