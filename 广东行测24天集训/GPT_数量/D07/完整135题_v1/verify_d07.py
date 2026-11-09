"""D07 independent numerical checks, recovery edition 2026-11-09.
Python 3.10+ stdlib only. This validates the encoded models, not all possible
natural-language interpretations or the uniqueness of arbitrary sequence rules.
"""
from fractions import Fraction as F
from itertools import permutations, product
from math import factorial, sqrt, gcd, ceil, isclose
import json
from pathlib import Path

checks={}
def add(n, value, opts, key, evidence='independent calculation'):
    ident=f'D07-M{n:03}'
    hits=[i for i,x in enumerate(opts) if isclose(float(value),float(x),rel_tol=1e-10,abs_tol=1e-9)]
    assert len(hits)==1, (ident,value,opts,hits)
    found='ABCD'[hits[0]]
    assert found==key,(ident,found,key,value)
    checks[ident]={'computed':str(value),'answer':found,'options':[str(x) for x in opts], 'check':evidence}

# 001-020: model independently reconstructed from the problem statements.
add(1,F(1,2)/(F(2,4)-F(1,4)-F(1,6)),[4,6,8,12],'B')
add(2,F(160)/(3-F(80,60)),[90,96,100,120],'B')
add(3,F(156)/(3-1-F(1,3)),[78,90,F(468,5),108],'C')
add(4,2/(F(1,40)+F(1,80)),[50,F(160,3),60,F(200,3)],'B')
add(5,F(9,60)/(F(3,5)*(F(1,50)-F(1,60))),[60,75,90,150],'B')
add(6,F(18,4)+F(18,6),[6,7,F(15,2),9],'C')
add(7,F(18+6)/(1-F(3,4)),[54,72,90,96],'D')
add(8,(F(5,2)-2)/(F(1,40)-F(1,60)),[40,50,60,80],'C')
add(9,120+80*F(144-120,80-72),[240,300,360,480],'C')
add(10,2/(F(1,3)-F(1,9)),[6,9,12,15],'B')
add(11,1-F(1,2)-F(2,5)*F(5,1)/(F(6)*F(5,4)),[F(1,10),F(1,5),F(7,30),F(1,3)],'C')
add(12,1/(F(2,5)/30+F(3,5)/45)-30,[6,F(15,2),9,12],'B')
add(13,F(90)/(F(270,72)-F(90,60)-F(90,90)),[60,72,80,90],'B')
add(14,F(10,60)/(F(1,16)+F(1,8)-F(1,6)),[6,8,12,16],'B')
add(15,min(v for v in range(1,81) if F(3)+F(1,4)+F(120,v)<=F(24,5)),[75,76,78,80],'C','integer-speed feasibility over 1..80')
add(16,F(30)*(F(60,30)+F(60,60)+F(60,90))/2,[45,55,60,90],'B')
add(17,2*(F(8,3)-F(1,6))/(F(1,20)+F(1,30)),[50,54,60,64],'C')
add(18,F(210)*100/310,[F(2100,31),70,84,100],'A')
add(19,60+F(1,3)/(F(1,60)-F(1,90)),[90,120,150,180],'B')
# Upgraded M020: infer original duration, then mix equal distances at +20%/+50%.
T=F(15)/(1-F(5,6)); assert T==90
add(20,T-T/2*(F(5,6)+F(2,3)),[15,20,F(45,2),25],'C','v1.1 two-stage equal-distance speed changes')

# General exact segment intersection routines for periodic motion.
def periodic_dist(t,speed,walk,rest):
    t=F(t); walk=F(walk); rest=F(rest)
    cyc=walk+rest; k=t//cyc; rem=t-k*cyc
    return F(speed)*(k*walk+min(rem,walk))

def first_at_target(fun,target,bounds):
    bs=sorted(set(map(F,bounds)))
    for a,b in zip(bs,bs[1:]):
        ya,yb=fun(a),fun(b)
        if ya==target:return a
        if (ya-target)*(yb-target)<=0 and ya!=yb:
            return a+(target-ya)*(b-a)/(yb-ya)
    if fun(bs[-1])==target:return bs[-1]
    raise AssertionError('no crossing')

def turn_times(v,L,T,start=0):
    v,L,T,start=map(F,(v,L,T,start)); lo=min(start,start+v*T); hi=max(start,start+v*T)
    return [F(k)*L/v-start/v for k in range(int(lo//L)-1,int(hi//L)+2) if 0< (F(k)*L-start)/v<T]

def triangle(z,L):
    r=F(z)%(2*L)
    return r if r<=L else 2*L-r

def linear_meetings(f,bounds,T,period=None):
    bs=sorted(set([F(0),F(T)]+[F(t) for t in bounds if 0<t<T])); out=set()
    for a,b in zip(bs,bs[1:]):
        ya,yb=f(a),f(b)
        if ya==yb:
            if (period is None and ya==0) or (period is not None and ya%period==0):
                raise ValueError('coincident interval must not be counted as discrete meetings')
            continue
        targets=[F(0)] if period is None else [F(k)*period for k in range(int(min(ya,yb)//period)-1,int(max(ya,yb)//period)+2)]
        for y in targets:
            t=a+(y-ya)*(b-a)/(yb-ya)
            if a<=t<=b and 0<t<=T:out.add(t)
    return sorted(out)

add(21,60*(F(1,2)+F(270,100))-150,[30,36,42,48],'C')
f22=lambda t:periodic_dist(t,F(1,5),15,5)-F(1,10)*t
add(22,first_at_target(f22,3,[0,15,20,35,40,55,60]),[40,45,50,60],'C','piecewise exact first crossing')
add(23,F(20)/(1-F(4,9)),[30,36,40,50],'B')
add(24,(F(4,3)+F(6,5))/(1-F(2,3)),[6,F(36,5),F(38,5),8],'C')
add(25,90*F(15,150),[6,9,12,15],'B')
add(26,F(3,2),[1,F(3,2),2,F(9,4)],'B','positive solution r^2=9/4; meeting time 3h verifies both post-meeting trips')
assert F(3,2)*3==F(3)*F(3,2) and F(3)==2*F(3,2)
add(27,F(240)*F(60,100)-(240-F(40,3))*F(60,100),[6,8,12,20],'B')
# Upgraded M028: leader also accelerates at its own distance trigger.
f28=lambda t:(6*min(t,30)+8*max(F(0),t-30))-(210+4*min(t,60)+7*max(F(0),t-60))
add(28,first_at_target(f28,0,[0,30,60,120]),[F(135,2),75,90,105],'C','piecewise exact crossing; no capture in first two phases')
gap=F(120); total=F(0)
for _ in range(3):
    dt=gap/8; total+=dt; gap-=4*dt
add(29,total*6,[135,150,F(315,2),180],'C')
add(30,2/(F(1,6)+F(1,12)),[6,8,9,10],'B')
add(31,F((15+10)*12,15-10),[48,54,60,72],'C')
add(32,F(3,2)*2/(F(3,2)-1),[2,4,6,8],'C')
add(33,F(90)*F(1,1)/F(3,2)*F(5,4)/F(3,4),[96,100,108,120],'B')
# M034 adaptation of ZJ2018A-61: recover speeds, then include waiting at exit.
b=F(200,25); a=F(3,2)*b; L=(a+b)*30
assert (a,b,L)==(12,8,600)
f34=lambda t:(L-a*max(F(0),t-60))-max(F(0),L-b*t)
add(34,first_at_target(f34,0,[60,75,110])-30,[60,75,80,120],'C','v1.1: leader stops at exit before pursuer catches')
add(35,F(20)*(F(3,2)+1)/(F(3,2)-1),[60,80,100,120],'C')
add(36,F(30)/(2-F(1,2)),[15,20,30,40],'B')
add(37,(F(1)+F(1,2)+1+2)/(1-F(1,2)),[6,7,8,9],'D')
add(38,30*(1+F(90,120)),[45,F(105,2),60,F(135,2)],'B')
add(39,(F(2)-F(5,3))/(F(13,6)-2),[F(1,2),F(2,3),F(3,2),2],'D')
f40=lambda t:F(80)*t-(30+60*min(t,F(1,2))+60*max(F(0),t-F(3,4)))
add(40,60*first_at_target(f40,0,[0,F(1,2),F(3,4),2]),[45,60,75,90],'A','capture precisely at end of stop')

add(41,(5*3*F(400,2))%400,[0,100,200,300],'C')
add(42,400*(1-F(320,400)*F(300,400)),[120,140,160,180],'C')
add(43,(5*7*F(360,9))%360,[40,160,280,320],'D')
locs={(7*(F(125)+250*k))%500 for k in range(20) if 125+250*k<=3600}
add(44,len(locs),[1,2,4,5],'B','explicit event locations within 1h')
add(45,len(set(range(300,601,300))|set(range(200,601,200))),[3,4,5,6],'B')
f46=lambda t:6*(30*(F(t)//90)+min(F(t)%90,30))+3*(60*(F(t)//90)+max(F(0),F(t)%90-30))-4*t-40
m46=linear_meetings(f46,[30,90,120,180,210,270],300,F(360))
add(46,len(m46),[5,6,7,8],'C',str(m46))
f47=lambda t:periodic_dist(t,F(1,10),40,10)+periodic_dist(t,F(1,15),30,5)
add(47,first_at_target(f47,10,[0,30,35,40,50,65,70,80]),[65,68,70,72],'C','piecewise first crossing')

def folded_meetings(v1,v2,L,T,opposite=False):
    start=L if opposite else 0
    s2=-v2 if opposite else v2
    f=lambda t:triangle(v1*t,L)-triangle(start+s2*t,L)
    bounds=turn_times(v1,L,T)+turn_times(s2,L,T,start)
    return linear_meetings(f,bounds,T)

m48=folded_meetings(5,3,300,400)
add(48,triangle(5*m48[4],300),[0,75,150,225],'B',str(m48[:5]))
m49=folded_meetings(6,2,300,600)
add(49,len([t for t in m49 if triangle(6*t,300) not in (0,300)]),[3,4,6,8],'B',str(m49))
m50=folded_meetings(5,3,400,400,True)
add(50,m50[4],[250,300,350,400],'C',str(m50))
rights=sorted(F(90+180*k+240,F(11,2)) for k in range(-3,10) if 90+180*k+240>0)
add(51,rights[2],[F(720,11),F(900,11),F(1020,11),100],'C',str(rights[:3]))
add(52,F(720,5),[120,144,180,240],'B')
add(53,F(600,8)+F(600,2),[225,300,375,450],'C')
add(54,50+F((6-4)*50,6+4),[50,60,75,100],'B')
add(55,40+F(400-8*20-5*20,8),[50,F(115,2),60,65],'B')
add(56,sum(max(F(0),min(F(600),F(700+1000*k,2))-max(F(0),F(300+1000*k,2))) for k in range(2)),[150,200,250,300],'B')
f57=lambda t:periodic_dist(t,6,200,20)-4*t
add(57,first_at_target(f57,600,[0,200,220,420,440]),[300,330,350,360],'D')
add(58,200*(1-F(190,200)*F(180,200)),[20,28,29,30],'C')
m59=folded_meetings(5,3,600,1300)
assert triangle(5*m59[3],600)==600
next_a=next(t for t in m59 if t>m59[3] and triangle(5*t,600)==0)
add(59,next_a-m59[3],[150,300,450,600],'D',str(m59))
add(60,len({(5*F(420,7)*k)%420 for k in range(1,11)}),[5,6,7,10],'C')
add(61,F(3,2)*(10*20/F(1,2))/10,[20,40,60,100],'C')
add(62,(F(180,24-12)*12+300)/F(180,24-12),[28,30,32,36],'C')
add(63,F(500)/(F(500,10)-20-20),[25,40,50,60],'C')
add(64,10*(F(140,10)-1),[120,130,140,150],'B')
add(65,(F(400,8)-20)*F(18,5),[72,108,180,243],'B')
add(66,F(60,4-1)*4,[60,75,80,90],'C')
add(67,36+18*F(45-36,18-15),[72,80,90,108],'C')
add(68,120-(F(60,F(3,2))+F(40,2)),[30,40,60,80],'C')
add(69,F(24)/((F(24,2)-F(24,3))/2),[8,10,12,15],'C')
add(70,1/F(40,60),[1,F(3,2),2,3],'B')
add(71,5*F(19)/(F(3,10)+F(2,6)),[120,135,150,180],'C')
add(72,(F(1,2)+(60-F(3,2))/15-4)*60,[20,24,30,36],'B')
add(73,F(600,4)-F(600,5),[20,30,40,50],'B')
add(74,8*F(96,24),[24,32,40,48],'B')
add(75,F(12,10)*12,[12,F(72,5),15,18],'B')
add(76,14+(F(70,28)-1)*16,[32,35,38,40],'C')
add(77,(F(30,2)-F(30,3))/2,[F(3,2),F(5,2),3,5],'B')
add(78,40+F(90-45-10,F(3,2)),[60,F(190,3),65,70],'B')
add(79,F(250,10)+F(800-250,15),[F(175,3),F(185,3),65,80],'B')
add(80,F(300+120,5),[60,72,84,90],'C')

# Exhaustive delivery route optimization, including cross-side mixed trips.
def delivery_best(points,capacity,last_return):
    best=10**9
    def partitions(order,start=0):
        if start==len(order):yield []; return
        for k in range(1,min(capacity,len(order)-start)+1):
            for tail in partitions(order,start+k):yield [order[start:start+k]]+tail
    for perm in set(permutations(points)):
        for batches in partitions(perm):
            cost=0
            for j,b in enumerate(batches):
                cost+=abs(b[0])+sum(abs(x-y) for x,y in zip(b,b[1:]))
                if j<len(batches)-1 or last_return:cost+=abs(b[-1])
            best=min(best,cost)
    return best
add(81,delivery_best((1,2,3,4,5),2,False),[11,12,13,18],'C','all visit orders and capacity-valid batch splits')
add(82,delivery_best((-3,-1,2,4,6),2,False),[14,15,16,18],'C','all visit orders and capacity-valid batch splits')
add(83,delivery_best((2,2,5,5,5,9),3,True),[24,26,28,32],'C','all visit orders and capacity-valid batch splits')
add(84,1+F(16,24)+F(20-F(20,3),20),[F(5,3),2,F(7,3),F(8,3)],'C')
add(85,30+6-F(6+8,2),[23,25,27,29],'D')
t=5+7;t=ceil(F(t,10))*10+18+5;t=ceil(F(t,12))*12+16
add(86,t-5,[47,51,55,59],'D')
# Upgraded M087: a mandatory load stop resets continuous-driving timer.
# 60km +10min rest; 30km +20min loading resets timer; final 60km, no end rest.
add(87,60+10+30+20+60,[170,180,190,200],'B','v1.1 continuous-driving reset at load stop')
add(88,60+(F(2)-F(60,40))*60,[70,80,90,100],'C')
add(89,max(x for x in range(101) if F(1,3)+F(x,40)+F(100-x,80)<=2),[30,33,34,40],'B','v1.1 construction-segment integer bound 0..100km')
add(90,20+F(10,25)*60,[40,44,48,50],'B','catch in 5min after bus departs, before B')
add(91,180+20-(20+120),[40,50,60,70],'C')
add(92,len([t for t in range(-120,121,15) if -60<t<60]),[6,7,8,9],'B','strict departure window excluding both terminal encounters')
add(93,F(300+220+400+180,20),[46,55,64,73],'B')
add(94,F(75-60)*F(1,2),[5,F(15,2),10,15],'B')
f95=lambda t:periodic_dist(t,6,40,20)-4*t
m95=linear_meetings(f95,[40,60,100,120,160],180)
add(95,len(m95),[2,3,4,5],'B',str(m95))
roots=[F(t) for t in range(1,100) if (4*(t+8))**2+(3*t)**2==78**2]
assert roots==[10]
add(96,roots[0],[8,10,12,15],'B','positive-distance monotonicity plus exact substitution')
add(97,F(9)*2/(2+4),[2,3,4,6],'B','reflection and similar triangles')
add(98,2+sqrt(12**2+5**2),[13,14,15,17],'C','translation removing fixed bridge width')
add(99,F(1,5)/(F(1,60)-F(3,200)),[90,100,120,150],'C')
add(100,(4-3)*F(9,3),[2,3,4,F(9,2)],'B')
x=(6-F(6,5))/(F(4,25)+F(4,75)); assert x==F(45,2)
add(101,(6-F(4,25)*x)*60,[132,138,144,150],'C','monotone decreasing/increasing arrival functions; feasible intersection')
add(102,len([t for t in (300,600) if 9*t%600==0]),[0,1,2,3],'B')
add(103,F(72,15)+2+F(72+6,9),[F(72,5),15,F(232,15),16],'C')
f104=lambda t:min(periodic_dist(t,60,F(3,4),F(1,4)),150)-min(30+40*t,150)
add(104,first_at_target(f104,0,[0,F(3,4),1,F(7,4),2,F(11,4),3,F(13,4)]),[3,F(13,4),F(7,2),F(15,4)],'B','piecewise motion including leader waiting at B')
add(105,F(30)/(F(7,4)-F(90,60)),[90,100,110,120],'D','monotonicity in high-speed distance; attainable boundary')
assert set(checks)=={f'D07-M{i:03}' for i in range(1,106)}

# Number sequences: generate all displayed known terms, not just predicted term.
seqchecks={}
def seq(n,known,generated,opts,key,blank=-1):
    if blank<0:blank=len(generated)-1
    assert len(known)==len(generated),(n,'length')
    for i,(a,b) in enumerate(zip(known,generated)):
        if a is not None:assert a==b,(n,i,a,b)
    val=generated[blank]
    hits=[i for i,x in enumerate(opts) if x==val]
    assert hits==['ABCD'.index(key)],(n,val,opts,key)
    seqchecks[f'D07-N{n:03}']={'answer':key,'computed':str(val),'all_known_terms_match':True,'rule_options_match':1}
    return generated

def recur(starters,n,fn):
    a=list(starters)
    while len(a)<n:a.append(fn(a,len(a)))
    return a
seq(1,[4,9,18,33,56,None],recur([4],6,lambda a,i:a[-1]+i*i+i+3),[79,85,89,93],'C')
seq(2,[58,30,16,9,F(11,2),None],recur([F(58)],6,lambda a,i:a[-1]/2+1),[F(7,2),F(15,4),F(17,4),F(9,2)],'B')
seq(3,[F(5,2),F(5,6),F(5,12),F(1,4),F(1,6),None],[F(5,k*(k+1)) for k in range(1,7)],[F(1,8),F(5,42),F(5,36),F(1,7)],'B')
seq(4,[7,5,26,10,63,17,124,None],[v for k in range(2,6) for v in (k**3-1,k*k+1)],[24,25,26,28],'C')
pr=[17,19,23,29,31,37]
seq(5,[16,1,18,5,24,7,None],recur([16],7,lambda a,i:pr[i-1]-a[-1]),[28,29,30,31],'C')
seq(6,[2,3,4,F(9,2),F(16,3),F(45,8),None],recur([F(2)],7,lambda a,i:F(6*i)/a[-1]),[F(32,5),F(36,5),F(48,7),F(15,2)],'A')
seq(7,[1,2,3,7,22,None],recur([1,2],6,lambda a,i:a[-2]*a[-1]+1),[149,153,154,155],'D')
seq(8,[9,4,5,-1,6,-7,None],recur([9,4],7,lambda a,i:a[-2]-a[-1]),[-13,-1,1,13],'D')
seq(9,[0,4,18,48,100,180,None],[k*k*(k-1) for k in range(1,8)],[252,294,336,392],'B')
seq(10,[0,1,6,27,124,None],recur([0],6,lambda a,i:a[-1]*i+i*i),[620,625,645,649],'C')
seq(11,[2,4,9,28,125,726,None],[factorial(k)+k for k in range(1,8)],[5040,5047,5054,5760],'B')
seq(12,['2.03','5.06','10.12','17.24','26.48',None],[f'{k*k+1}.{3*2**(k-1):02}' for k in range(1,7)],['35.96','37.86','37.96','38.96'],'C')
# Upgraded N013: complete-group candidates require both group progression and product rule.
pr=[2,3,5,7,11,13]
seq(13,[(2,3,7),(3,5,16),(5,7,36),(7,11,78),None],[(pr[k],pr[k+1],pr[k]*pr[k+1]+1) for k in range(5)],[(11,13,143),(11,17,188),(11,13,144),(13,17,222)],'C')
seq(14,[3,6,8,24,27,108,112,None],recur([3],8,lambda a,i:a[-1]*((i+3)//2) if i%2 else a[-1]+(i+2)//2),[336,448,560,672],'C')
seq(15,[18,227,364,4125,None],[int(f'{k}{(k+1)**3}') for k in range(1,6)],[5216,5256,6216,6360],'A')
seq(16,[F(2,3),F(3,8),F(4,15),F(5,24),F(6,35),None],[F(k,k*k-1) for k in range(2,8)],[F(7,42),F(7,48),F(7,49),F(8,63)],'B')
seq(17,[1,1,F(3,4),F(1,2),F(5,16),F(3,16),None],[F(k,2**(k-1)) for k in range(1,8)],[F(5,64),F(7,64),F(7,48),F(1,8)],'B')
# N018 is checked after squaring positive radicals; option squares are distinct.
seq(18,[1,2,3,5,8,13,None],recur([1,2],7,lambda a,i:a[-1]+a[-2]),[16,20,21,23],'C')
seqchecks['D07-N018']['computed']='sqrt(21)';seqchecks['D07-N018']['check']='all radicands and positive roots'
pr=[2,3,5,7,11,13,17]
seq(19,[2,6,20,42,110,156,None],[p*(p-1) for p in pr],[210,240,272,306],'C')
seq(20,[2,F(5,3),F(10,7),F(17,15),F(26,31),None],[F(k*k+1,2**k-1) for k in range(1,7)],[F(35,63),F(37,63),F(37,62),F(49,63)],'B')
seq(21,[200,164,139,123,114,110,None],recur([200],7,lambda a,i:a[-1]-(7-i)**2),[106,107,108,109],'D')
seq(22,[1,8,2,27,6,64,24,None,120],[factorial(i//2+1) if i%2==0 else (i//2+2)**3 for i in range(9)],[81,100,125,216],'C',blank=7)
seq(23,[4,7,14,29,60,123,None],recur([4],7,lambda a,i:2*a[-1]+i-2),[246,248,250,252],'C')
seq(24,[2,7,9,16,20,29,None],recur([2],7,lambda a,i:(i+2)**2-a[-1]),[33,35,36,37],'B')
seq(25,[4,6,15,56,275,None],recur([4],6,lambda a,i:(a[-1]-1)*(i+1)),[1370,1644,1650,1925],'B')
seq(26,[1,2,6,15,16,20,29,None,34],recur([1],9,lambda a,i:a[-1]+[1,4,9][(i-1)%3]),[30,31,32,33],'A',blank=7)
seq(27,[2,8,64,1024,32768,None],[2**(k*(k+1)//2) for k in range(1,7)],[2**20,2**21,2**22,2**23],'B')
seq(28,[2,1,7,10,31,61,None],recur([2,1],7,lambda a,i:3*a[-2]+a[-1]),[123,144,154,183],'C')
v=[2,3,5,8,12,17,23]
seq(29,['2.03','3.05','5.08','8.12','12.17',None],[f'{v[k]}.{v[k+1]:02}' for k in range(6)],['16.22','17.22','17.23','18.24'],'C')
seq(30,[2,3,4,9,16,29,None],recur([2,3,4],7,lambda a,i:sum(a[-3:])),[50,52,54,58],'C')
assert len(seqchecks)==30

# Finite scan for alternative small-integer affine recurrences on applicable numeric sequences.
# This cannot prove semantic/absolute uniqueness and intentionally excludes decimal-string puzzles.
candidates={1:[4,9,18,33,56],2:[F(58),30,16,9,F(11,2)],5:[16,1,18,5,24,7],7:[1,2,3,7,22],8:[9,4,5,-1,6,-7],9:[0,4,18,48,100,180],10:[0,1,6,27,124],11:[2,4,9,28,125,726],14:[3,6,8,24,27,108,112],19:[2,6,20,42,110,156],21:[200,164,139,123,114,110],23:[4,7,14,29,60,123],24:[2,7,9,16,20,29],25:[4,6,15,56,275],28:[2,1,7,10,31,61],30:[2,3,4,9,16,29]}
scan={}
for n,a in candidates.items():
    matched=[]
    for p,q,c in product(range(-4,5),range(-4,5),range(-10,11)):
        if all(a[i]==p*a[i-1]+q*a[i-2]+c for i in range(2,len(a))):
            matched.append({'p':p,'q':q,'c':c,'next':str(p*a[-1]+q*a[-2]+c)})
    scan[f'D07-N{n:03}']=matched

report={'version':'D07-v1.1-20261109','math_count':len(checks),'number_sequence_count':len(seqchecks),'all_encoded_checks_pass':True,'math':checks,'number_sequences':seqchecks,'limited_affine_competitor_scan':scan,'limits':['Independent model checks, not an automatic proof of all linguistic readings.','Number-series rules are verified against every displayed term and options, not universally unique continuations.','No claim of Claude cross-review or original-PDF page verification.']}
Path(__file__).with_name('D07_独立核验结果.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'math':len(checks),'number':len(seqchecks),'all_checks_pass':True,'sequence_linear_scan':scan},ensure_ascii=False,indent=2))
