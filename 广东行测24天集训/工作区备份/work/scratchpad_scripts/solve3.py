from fractions import Fraction as F
from itertools import product, combinations
from functools import lru_cache
res={}
# M097: weekday 0=Mon..6=Sun ; Tue(1),Thu(3),Sat(5) keep 2/3 ; others keep 1/2
def keep(wd, sunday_rule='half'):
    if wd in (1,3,5): return F(2,3)
    if wd==6 and sunday_rule=='none': return F(1)
    return F(1,2)
for rule in ['half','none']:
    out=[]
    for start in range(7):
        f=F(1)
        for i in range(6): f*=keep((start+i)%7,rule)
        out.append((start,f,F(1,72)/f))
    res['M097_'+rule]=(out,max(t[2] for t in out))
# M098
M=F(4)/(F(1)/F(12,10)-F(1)/F(15,10)); J=M/F(12,10); Fe=M/F(15,10); A=4*M-J-Fe-M
res['M098']=(M,J,Fe,A,A/Fe-1)
# M099 integer days brute force: choose days T, 甲 t1 days on A, 乙 t2 days on A
best=None
for T in range(1,60):
    ok=False
    for t1 in range(0,T+1):
        for t2 in range(0,T+1):
            Aa=6*t1+1*t2; Bb=3*(T-t1)+2*(T-t2)
            if Aa>=120 and Bb>=80: ok=True;sol=(t1,t2,Aa,Bb);break
        if ok: break
    if ok: best=(T,sol);break
res['M099_int']=best
# continuous LP via fine grid
best=None
for T2 in range(2*1,2*60):
    T=F(T2,2)
    # for given T, maximize B subject to A>=120: 甲 relatively better at A (6/3=2 vs 1/2)
    # 甲 does A first
    t1=min(T,F(120,6)); Arem=120-6*t1; t2=Arem/1 if Arem>0 else 0
    if t2>T: continue
    Bb=3*(T-t1)+2*(T-t2)
    if Bb>=80: best=T;break
res['M099_half']=best
# M100
app=[2,6,10,12,15,25]
best=None
for mask in range(64):
    A=[app[i] for i in range(6) if mask>>i&1]
    Mm=[app[i] for i in range(6) if not mask>>i&1]
    ms=max(F(sum(A)),F(sum(Mm))/F(3,2))
    if best is None or ms<best[0]: best=(ms,A,Mm)
res['M100']=best
# M101 LP check: 乙 rates a (A), b (B); 甲 2a, 3b. Given a/b=r, compute optimal and 甲 output
def opt101(r):
    # set b=1, a=r, X=1. 甲 does B first(comparative adv 3>2). find T minimal
    a=F(r); b=F(1)
    # case1: 甲 all B, plus some A; 乙 only A
    # 甲 time: 1/(3b) + xA/(2a) ; 乙: (1-xA)/a ; equalize
    # 1/3 + xA/(2a) = (1-xA)/a -> xA(1/(2a)+1/a) = 1/a - 1/3
    xA=(1/a-F(1,3))/(F(1,2)/a+1/a)
    if 0<=xA<=1:
        T=F(1,3)+xA/(2*a)
        return ('case1',T,1+xA)
    # case2: 乙 all A, plus some B; 甲 only B
    # 乙: 1/a + yB/b ; 甲: (1-yB)/(3b)
    yB=(F(1,3)-1/a)/(1+F(1,3))
    T=1/a+yB
    return ('case2',T,1-yB)
res['M101']=[(r,opt101(r)) for r in [F(3,4),F(3,5),F(4,3),F(5,3)]]
# M102: maximize valid fraction v: 2v+5(1-v)>=2.9 and feasibility
votes=[69,63,44,58,56]
best=None
for v in range(0,101):
    inv=100-v
    # invalid ballots each choose 3..5; valid choose 1..2. need total selections 290
    lo=v*1+inv*3; hi=v*2+inv*5
    if not (lo<=290<=hi): continue
    # each work count from invalid <= inv, from valid <= v
    if all(x<=v+inv for x in votes):
        best=v
res['M102']=best
# feasibility at v=70: invalid 30 choose all 5 -> residual
r=[x-30 for x in votes]; res['M102_resid']=(r,sum(r),max(r)<=sum(r)-max(r))
# M103 simulation per hour, find r from day14, then first time diff>=100 continuous
def cum(t,r):
    # t real hours
    import math
    full=int(t//4); rem=t-4*full
    jia=5*r*(full+min(rem,1)); yi=r*t
    return jia-yi
r=F(60)/(cum(F(14),F(1)))
res['M103_r']=r
first=None
t=F(0)
step=F(1,100)
while t<40:
    if cum(t,r)>=100: first=t;break
    t+=step
res['M103']=(first,[ (h,cum(F(h),r)) for h in range(1,30)])
# M105
cnt=0;sols=[]
for a1,b1,c1 in product(range(1,6),repeat=3):
    if a1+b1+c1!=5: continue
    for a2,b2,c2 in product(range(1,6),repeat=3):
        if a2+b2+c2!=5: continue
        if a1+a2>b1+b2 and a1+a2>c1+c2 and b1>b2:
            cnt+=1;sols.append(((a1,a2),(b1,b2),(c1,c2)))
res['M105']=(cnt,sols)
for k_,v_ in res.items(): print(k_,v_)
