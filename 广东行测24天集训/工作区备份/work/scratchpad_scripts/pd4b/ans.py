# print analysis text for keys. usage: ans.py KEY [KEY...] [--n=1800]
import sys, re
sys.path.insert(0,'/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pd4b')
from ans_lib import load
n=1600
keys=[]
for a in sys.argv[1:]:
    if a.startswith('--n='): n=int(a[4:])
    else: keys.append(a)
def pats(q):
    return [r'【\s*题目\s*%d\s*】'%q, r'【解析\s*%d\s*[—\-–]'%q, r'题目\s*%d\s*解析'%q, r'【\s*%d\s*】'%q, r'(?:^|\n)\s*第\s*%d\s*题'%q,
            r'(?:^|\n)\s*%d\s*[\.、．:：]\s*(?:正确答案|【答案】|答案|解析|第一步|\n)'%q,
            r'(?:^|\n)\s*%d\s*(?:\n|\s)\s*(?:正确答案|【答案】|答案|解析|第一步)'%q,
            r'(?:^|\n)\s*%d\s*[\.、．:：]'%q]
for key in keys:
    pid,q=key.rsplit('-',1); q=int(q)
    f,full,offs=load(pid)
    print('='*10,key,'|',f)
    if not f: print('NO ANALYSIS FILE'); continue
    if len(full)<2000: print('NO TEXT LAYER (scan), chars=',len(full)); continue
    best=None
    for p in pats(q):
        for m in re.finditer(p,full):
            seg=full[m.start():m.start()+500]
            if re.search(r'答案|解析|正确|第一步|论点|题干|排除|当选',seg):
                best=m.start(); break
        if best is not None: break
    if best is None: print('NO HIT'); continue
    # cut at next question marker
    seg=full[best:best+n]
    nxt=None
    for p in pats(q+1):
        m=re.search(p,seg[20:])
        if m: nxt=m.start()+20 if nxt is None else min(nxt,m.start()+20)
    if nxt: seg=seg[:nxt]
    pg=max(i for i,o in enumerate(offs) if o<=best)+1
    print('----- page',pg); print(seg.strip())
