"""D07 v2: independent exact checks of the 36 replacement models and N007.
No claim is made that numerical checking proves every natural-language reading.
All arithmetic uses fractions; event roots are solved on linear segments.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json, math
R={}
def save(n,v,e):
    R[f'M{n:03}']={'value':str(v),'evidence':e}
    return v

def eq(v,w):
    assert v==w,(v,w)

def cyc_roots(breaks,linear,L):
    # linear(t midpoint) returns slope,intercept for the relative unfolded position.
    out=set()
    for a,b in zip(breaks,breaks[1:]):
        m,c=linear((a+b)/2)
        if not m:
            assert c%L!=0, 'positive-length coincident interval needs separate handling'
            continue
        vals=[m*a+c,m*b+c]
        lo=math.floor(min(vals)/L)-1; hi=math.ceil(max(vals)/L)+1
        for k in range(lo,hi+1):
            t=(k*L-c)/m
            if a<=t<=b and t>0: out.add(t)
    return sorted(out)

def lin_at(segments,t):
    for a,b,m,c in segments:
        if a<=t<b: return m,c
    return segments[-1][2:]

def common_roots(s1,s2,H,exclude_zero=True):
    bs=sorted({F(0),F(H),*[x for s in s1+s2 for x in s[:2] if 0<=x<=H]})
    roots=set()
    for a,b in zip(bs,bs[1:]):
        m1,c1=lin_at(s1,(a+b)/2); m2,c2=lin_at(s2,(a+b)/2)
        if m1==m2:
            if c1==c2: roots.add(a)
        else:
            t=(c2-c1)/(m1-m2)
            if a<=t<=b: roots.add(t)
    return sorted(t for t in roots if (t>0 if exclude_zero else t>=0))

eq(save(2,F(90)/(F(19,4)-2-F(1,4)-F(3,2)),'three 90-km legs; two distinct delays'),90)
feasible=[v for v in range(1,101) if F(60,v)<=F(48,60)]
eq(save(3,min(feasible),'gate by 10:00; later release misses the deadline'),75)
x=(F(1)+3)*4
eq(x,16)
eq(save(6,x/4+(24-x)/8+F(1,3)+(24-x)/3+x/8,'outbound slope inferred under normal return; actual return uses other uphill section'),10)
x=(F(4)+F(1,4)-F(15,4))/(F(1,60)-F(1,90));eq(x,90)
eq(save(8,x,'fixed five-minute permission cost included; length <=120'),90)
s=F(1,5)/(F(1,48)-F(1,80)-F(1,150));eq(save(12,s,'distance weights outside; time weights inside'),120)
x=(F(3,2)-F(60,50))/(F(1,50)-F(1,60));y=(F(3)+F(1,5)-F(150,50))/(F(1,50)-F(1,75))
eq(save(13,60+x+y,'two cumulative averages with distinct stop inclusion'),180)
valid=[v for v in [20,18,16,15] if 30*(F(1,2)+F(10,v))==2*v-10]
eq(save(17,valid[0],'all four speeds substituted; unique positive permitted option'),20);assert len(valid)==1
# five(x/60+.5)=three(x/60+.5+(270-x)/90)
x=(F(3)*F(270,90)-1)/(F(2,60)+F(3,90));eq(save(18,x,'departure from P includes service, not just arrival'),120)
t_after= (300-120-40*F(3,2)-40*F(1,3))/100
x=120+60*t_after;eq(save(27,x-180,'meeting after甲 resumes; shift measured from planned A-coordinate'),4)
roots=[]
for k in range(1,10):
    # buses x=3t-24k, rider x=0 for9min then t-9
    t=F(24*k,3)
    if 0<t<=9: roots.append(t)
    t=F(24*k-9,2)
    if t>=9: roots.append(t)
eq(save(31,sum(t<=24 for t in roots),'bus roots '+str(roots)),2)
valid=[]
for v in range(1,81):
    # All candidates within speed bound reach checkpoint behind甲.
    if v>50:
        pre=F(25,v-50)
        if v*pre<=50: t=F(1,2)+pre
        else: t=F(3*v,4)/(v-50) # v(t-.5-.25)=50t
        if t<=F(11,4): valid.append(v)
eq(save(33,min(valid),'integer scan1..80; checkpoint-before-catch checked'),69)
x=F(70);eq(40*(x/60+F(1,12)),x-20);save(35,x,'equation with乙30-minute delayed start; no coincidence at terminal pause')
A=[(F(0),F(2),F(60),F(0)),(F(2),F(9,4),F(0),F(120)),(F(9,4),F(5),F(80),F(-60))]
B=[(F(0),F(5,2),F(-40),F(310)),(F(5,2),F(5),F(-60),F(360))]
t=common_roots(A,B,5)[0];eq(t,3);eq(save(38,80*t-60,'all stages scanned; first root t=3h'),180)
r=F(1200-500,1)/(F(1200)/F(6,5));eq(save(41,600*(1-r),'infer乙/甲原速 from whole-lap second chase'),180)
pb=F(8)*F(4,5)*(75-10); pc=60+300+F(8)*F(4,5)*F(3,4)*F(5,4)*(75-F(300)/(F(8)*F(4,5)*F(3,4)))
eq(save(42,pc-pb,'separate start times, handicap and own-distance speed trigger'),19)
# source invariant for first point on the valid side, algebra plus representative exact simulations
for x in [F(1000),F(2000),F(4000),F(10000)]:
    L=3*x; va=x+500; vb=2*x-500
    rs=cyc_roots([F(0),F(4)],lambda t:(va+vb,-L),2*L)+cyc_roots([F(0),F(4)],lambda t:(va-vb,L),2*L)
    rs=sorted(set(rs))
    assert rs[0]==1 and rs[1]==3,(x,rs)
    def fold(u):
        z=u%(2*L);return z if z<=L else 2*L-z
    eq(L-fold(va*rs[1]),1500)
save(43,1500,'second encounter, not merely second head-on: invalid-side case excluded algebraically')
bs=list(map(F,[0,180,210,400]))
def oth(t): return (F(4),F(0)) if t<180 else ((F(0),F(720)) if t<210 else (F(4),F(-120)))
rs=[]
for sign in [-1,1]:
    def fun(t):
        m,c=oth(t);return F(6)+sign*m,sign*c
    rs+=cyc_roots(bs,fun,F(720))
rs=sorted(set(rs));eq(rs[:4],list(map(F,[72,144,228,300])))
z=(6*rs[3])%720;pos=z if z<=360 else 720-z
eq(save(48,pos,'folded-position roots '+str(rs[:5])),360)
real=F(325,65); phase=10*real-30; total=real+(720-phase)/10
eq(save(52,total,'shown time -> real trigger; then modulo720 display minutes'),75)
rs=cyc_roots(list(map(F,[0,60,80,700])),lambda t: (F(10),F(0)) if t<60 else ((F(6),F(240)) if t<80 else (F(1),F(640))),F(600))
eq(rs[:2],list(map(F,[60,560])));save(53,rs[1],'cyclic relative-position roots '+str(rs[:2]))
rs=cyc_roots(list(map(F,[0,120,150,600])),lambda t: (F(2),F(0)) if t<120 else ((F(-10),F(1440)) if t<150 else (F(-2),F(240))),F(720))
eq(rs[:2],list(map(F,[144,480])));save(54,rs[1],'two different reversal triggers; roots '+str(rs[:2]))
def cyc_dist(t,run,rest,speed):
    n=t//(run+rest); r=t-n*(run+rest)
    return speed*(n*run+min(r,run))
bs=sorted(set([F(0),F(300)]+[F(x) for x in range(0,301) if x%60 in (0,40) or x%150 in (0,120)]))
def rel55(t):
    m=(6 if t%60<40 else 0)+(4 if t%150<120 else 0)
    d=cyc_dist(t,40,20,6)+cyc_dist(t,120,30,4)
    return F(m),d-m*t
rs=cyc_roots(bs,rel55,F(480));eq(rs[3],252);save(55,rs[3],'all exact cyclic roots '+str(rs))
pts=[(350*n)%600 for n in range(1,13)]
eq(save(60,sum(150<=p<=450 for p in pts),'positions '+str(pts)),7)
v=F(180,9); L=36*v+180
val=(L+180)/v+(120+L+180)/30;eq(save(62,val,'derive tunnel length from wholly-inside interval'),94)
rel=F(360,8); vb=rel-20; dt=90/rel+(600-90)/(15+vb)
eq(save(65,dt,'total relative length600; first90 before slowdown'),F(59,4))
vdown=F(60,3);vup=F(60,5); w=(vdown-vup)/2;u=(vdown+vup)/2; wn=w*F(3,2)
val=F(2)+F(1,3)+(60-2*vup+wn/3)/(u-wn)
eq(save(69,val*60,'return-time minutes; inferred v=16,u=4 then u=6'),368)
boat=(10+2)*F(1,3); box=2*F(1,2); chase=(boat-box)/10;total=F(1,2)+chase
neq=save(70,2*total,'boat fixed to shore during10min; catch uses relative speed10');eq(neq,F(8,5))
for u in [F(6),F(10),F(15),F(20)]:
    v=F(6*60,12)
    eq(6*(60-2*u),12*(v-u))
save(71,v,'water cancels in two inverse-current journeys with6h versus12h')
A=[(F(0),F(3),F(15),F(0)),(F(3),F(12),F(-5),F(60)),(F(12),F(20),F(0),F(0))]
B=[(F(0),F(1),F(0),F(90)),(F(1),F(10),F(-10),F(100)),(F(10),F(20),F(0),F(0))]
t=common_roots(A,B,10)[0];eq(save(74,t,'check no root before direction reversal; both still beforeA at t8'),8)
val=F(120,60)+F(180,90)+F(20,60);eq(save(88,val*60,'lower bound20min qualifying stop attained at P'),260)
ret_start=F(20,60)+F(12,20)+F(4,60);meet=ret_start+(12-4*ret_start)/(20+4);arr=meet+(12-4*meet)/20
eq(save(90,arr*60,'first overtake ignored, pickup on return, final delivery included'),100)
# travel segments in minutes and kilometres
A=[];t=F(0);x=F(0)
for j in range(6):
    A.append((t,t+30,F(1),x-t));t+=30;x+=30
    if j<5:A.append((t,t+6,F(0),x));t+=6
A.append((t,F(250),F(0),F(180)))
B=[(F(0),F(48),F(0),F(0)),(F(48),F(88),F(3,2),F(-72)),(F(88),F(100),F(0),F(60)),(F(100),F(180),F(3,2),F(-90)),(F(180),F(250),F(0),F(180))]
rs=common_roots(A,B,220);eq(rs[0],140);eq(save(91,rs[0]-48,'first position equality at minute140 from8:00; '+str(rs)),92)
dep=[394+17*n for n in range(30)] #6:34=394
ok=[s for s in dep if 402<s<564];eq(save(92,len(ok),'departure times '+str(ok)),9)
val=F(300+180,20)+F(220-180,10)+F(400+180,20);eq(save(93,val,'trigger intervals measured with different train endpoints'),57)
ok=[v for v in range(61,201) if F(2)<=F(180,v)<F(7,3)]
eq(save(99,len(ok),'integers '+str(ok)),13)
# measure intervals of |position difference| >=20, both terminals stop
A=[(F(0),F(5),F(40),F(0))]
B=[(F(0),F(1,2),F(0),F(0)),(F(1,2),F(3,2),F(80),F(-40)),(F(3,2),F(2),F(0),F(80)),(F(2),F(4),F(60),F(-40)),(F(4),F(5),F(0),F(200))]
bs=sorted(set([F(0),F(5)]+[z for s in B for z in s[:2]]));total=F(0);windows=[]
for a,b in zip(bs,bs[1:]):
    m1,c1=lin_at(A,(a+b)/2);m2,c2=lin_at(B,(a+b)/2);m=m1-m2;c=c1-c2
    cuts={a,b}
    if m:
        for target in (-20,20):
            z=(target-c)/m
            if a<z<b:cuts.add(z)
    cuts=sorted(cuts)
    for l,r in zip(cuts,cuts[1:]):
        if abs(m*(l+r)/2+c)>=20:total+=r-l;windows.append((str(l),str(r)))
eq(save(100,total*60,'distance windows '+str(windows)),90)
xa=(F(6)-F(19,14))/(F(4,25)+F(11,175));eq(xa,F(125,6))
meet=(2*xa+5)/28;ta=xa/25+(30-xa)/5;tb=meet+(30-3*meet)/25
assert 5<=xa<=25 and 3*(xa/25+F(1,5))<xa
eq(ta,tb);eq(save(101,ta*60,'minimax intersection; distinct walkers,12min fixed stop; x='+str(xa)),160)
# for the new N007: all terms, not only the last, follow mean of two previous terms
seq=[F(2),F(14),F(8),F(11),F(19,2),F(41,4)]
for a,b,c in zip(seq,seq[1:],seq[2:]):eq((a+b)/2,c)
n=(seq[-2]+seq[-1])/2;eq(n,F(79,8))
opts=[F(39,4),F(79,8),F(81,8),F(21,2)];assert [k for k,x in enumerate(opts) if x==n]==[1]
R['N007']={'value':str(n),'evidence':'each term is mean of previous two; alternative first-difference ratio -1/2 gives same next value'}
assert len(R)==37
if __name__=='__main__':
    out=Path(__file__).with_name('升级题复算结果.json')
    out.write_text(json.dumps({'checked':37,'scope':'36 replacement mathematical models + N007; wording remains human-reviewed','results':R},ensure_ascii=False,indent=2),encoding='utf-8')
    print('PASS',len(R)); print(json.dumps(R,ensure_ascii=False,indent=2))
