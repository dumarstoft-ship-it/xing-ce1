import sys, json, time
from fractions import Fraction as F
sys.path.insert(0, '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad')
import engine

def P(x):
    x=x.replace('−','-').strip()
    if '/' in x:
        a,b=x.split('/'); return F(int(a),int(b))
    return F(x)

Q={}
for line in open('/home/user/work/review_d04/blind_G4.jsonl',encoding='utf-8'):
    d=json.loads(line); Q[d['bid']]=d

def int_cands(seq, mult=20, cap=60000):
    M=max(abs(v) for v in seq if v is not None)
    R=int(min(cap, mult*M+100))
    return [F(i) for i in range(-R, R+1)]
def frac_cands(seq, maxden=40, mult=6):
    M=max(abs(v) for v in seq if v is not None)
    R=float(mult*M+3)
    out=set()
    for q in range(1,maxden+1):
        lim=int(R*q)
        for p in range(-lim,lim+1):
            out.add(F(p,q))
    return sorted(out, key=lambda x:(x.denominator,abs(x)))

def run(bid, seq_str=None, opts=None, cands=None, **kw):
    d=Q[bid]
    stem=seq_str or d['stem']
    parts=[p for p in stem.replace('，',',').split(',')]
    seq=[None if '（' in p else P(p) for p in parts]
    options={k:P(v) for k,v in (opts or d['options']).items()}
    if cands is None:
        if all(v.denominator==1 for v in seq if v is not None) and all(v.denominator==1 for v in options.values()):
            cands=int_cands(seq)
        else:
            cands=frac_cands(seq)
    t=time.time()
    print('=====',bid,stem,options)
    engine.search(seq,options,cands,**kw)
    print('  (%.1fs)'%(time.time()-t))

if __name__=='__main__':
    for bid in sys.argv[1:]:
        run(bid)
