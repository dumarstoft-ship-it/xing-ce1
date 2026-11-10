import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ansx import info, seg
from plan4 import PLAN, PXPLAN, META
import simcheck
PAT=[r'正确答案[：:]\s*([A-D])', r'故正确答案为\s*([A-D])', r'因此[，,]?\s*选择\s*([A-D])\s*选项', r'故本题答案为\s*([A-D])', r'正确选项为\s*([A-D])', r'故本题选\s*([A-D])', r'故选\s*([A-D])', r'【答案】\s*([A-D])', r'正确答案是[：:]?\s*【?\s*([A-D])']
def letters(s):
    f=[]
    for P in PAT:
        for m in re.finditer(P,s): f.append((m.start(),m.group(1)))
    return [x[1] for x in sorted(set(f))]
keys=[k for d in PLAN for k in PLAN[d]]+[k for d in PXPLAN for k in PXPLAN[d]]
for key in keys:
    tag,q=key.rsplit('-',1); q=int(q)
    if not os.path.exists(f'/home/user/work/answers/{tag}.json'): print(key,'NO ANSWER FILE (scan)'); continue
    r=info(tag,q)
    if not r: print(key,'NOT FOUND'); continue
    s=r['seg']; L=letters(s)
    auto=json.load(open(f'/home/user/work/answers/{tag}.json'))['answers'].get(str(q),{}).get('ans')
    tw=[]
    for c,t,qq,sec,_ in (simcheck.sims(tag,q) or []):
        if c<0.9: continue
        if os.path.exists(f'/home/user/work/answers/{t}.json'):
            try:
                rr=seg(t,qq); tw.append(f'{t}-{qq}:{rr["ans"] if rr else "?"}')
            except Exception as e: tw.append(f'{t}-{qq}:ERR')
        else: tw.append(f'{t}-{qq}:noans')
    exp=META.get(key,(None,None))[1]
    flag='' if (len(set(L))==1 and L[0]==auto and (exp is None or exp==L[0])) else '  <<<<< CHECK'
    print(key,'p',r['page'],'letters',''.join(L),'auto',auto,'exp',exp,'rate',r['rate'],r['yicuo'],'| twins',tw,'|',(r['chuchu'] or '')[:40],'| DISPUTE' if '争议' in s else '', '| seglen',len(s), flag)
