# Extra Q31: 4/3, 1/2, 1/2, 7/10, 7/9, ( )   options A 2/3  B 13/18  C 12/17  D 14/17
# Search "反约分" rules: scale each reduced fraction by k_i, then require numerators and
# denominators each to follow a simple pattern; report every prediction and which option it hits.
from fractions import Fraction as F
import itertools
terms=[(4,3),(1,2),(1,2),(7,10),(7,9)]
opts={'A':F(2,3),'B':F(13,18),'C':F(12,17),'D':F(14,17)}

def diffs(s): return [b-a for a,b in zip(s,s[1:])]
def predict(s):
    """return list of (rule, next value) for simple integer sequence s"""
    out=[]
    d=diffs(s)
    if len(set(d))==1: out.append(('arith d=%d'%d[0], s[-1]+d[0]))
    dd=diffs(d)
    if len(set(dd))==1 and dd[0]!=0: out.append(('2nd-order d2=%d'%dd[0], s[-1]+d[-1]+dd[0]))
    if all(x!=0 for x in d):
        r=[F(b,a) for a,b in zip(d,d[1:])]
        if len(set(r))==1 and r[0] not in (0,1) and r[0].denominator==1:
            out.append(('diff geometric r=%s'%r[0], s[-1]+d[-1]*r[0]))
    if all(x!=0 for x in s):
        r=[F(b,a) for a,b in zip(s,s[1:])]
        if len(set(r))==1 and r[0]!=1 and (s[-1]*r[0]).denominator==1:
            out.append(('geometric r=%s'%r[0], int(s[-1]*r[0])))
    # a_n = a_{n-1}*m + c   (linear recurrence with integer m in 2..3)
    for m in (2,3):
        c=[s[i+1]-m*s[i] for i in range(len(s)-1)]
        if len(set(c))==1: out.append(('x%d%+d'%(m,c[0]), m*s[-1]+c[0]))
    # Fibonacci-like a_n=a_{n-1}+a_{n-2}+c
    c=[s[i+2]-s[i+1]-s[i] for i in range(len(s)-2)]
    if len(set(c))==1: out.append(('fib%+d'%c[0], s[-1]+s[-2]+c[0]))
    return out

hits={}
for ks in itertools.product(range(1,13),repeat=5):
    N=[k*p for k,(p,q) in zip(ks,terms)]; D=[k*q for k,(p,q) in zip(ks,terms)]
    pn=predict(N); pd=predict(D)
    for (rn,vn),(rd,vd) in itertools.product(pn,pd):
        if vd==0: continue
        val=F(vn,vd)
        key=(tuple(N),tuple(D),rn,rd)
        hits[key]=val
for (N,D,rn,rd),val in sorted(hits.items(),key=lambda x:(x[0][0],x[0][1])):
    lab=[k for k,v in opts.items() if v==val]
    print('N',N,rn,'| D',D,rd,'->',val,lab)
print('total rules found:',len(hits))
