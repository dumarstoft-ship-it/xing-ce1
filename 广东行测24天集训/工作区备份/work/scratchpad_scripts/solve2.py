from fractions import Fraction as F
from itertools import product, combinations
import sympy as sp
res={}
# M081
c=sp.symbols('c')
res['M081']=sp.solve(sp.Eq(200*0.6*c+100*0.3*c+100*(-0.3)*c,15000),c)
# M082
P=sp.symbols('P')
res['M082']=sp.solve(sp.Eq(sp.Rational(6,10)*P+150,sp.Rational(14,10)*(sp.Rational(4,10)*P+150)),P)
# M083
E=sp.symbols('E')
e=sp.solve(sp.Eq(sp.Rational(1,10)*E+sp.Rational(3,10)*3*E,sp.Rational(600,400)),E)[0]
res['M083']=(e,3*e*sp.Rational(7,10)-e*sp.Rational(9,10))
# M084
a,b=sp.symbols('a b',positive=True)
prof0=10*sp.Rational(3,10)*a+4*sp.Rational(4,10)*b
setp=sp.Rational(9,10)*(a+b)-sp.Rational(7,10)*a-sp.Rational(6,10)*b
s=sp.solve(sp.Eq(8*setp,sp.Rational(12,10)*prof0),a)
res['M084']=s
# M085 two readings
c=sp.symbols('c')
u1=sum(40+10*k for k in range(1,16)); u2=sum(40+10*k for k in range(0,15))
res['M085']=(u1,sp.solve(sp.Eq(u1*(sp.Rational(8,10)-c),800*(1-c)),c),u2,sp.solve(sp.Eq(u2*(sp.Rational(8,10)-c),800*(1-c)),c))
# M086
def split86(T):
    T=F(T)
    s1=min(T,10); s2=min(max(T-10,0),10); s3=max(T-20,0)
    jia=F(8,10)*s1+F(6,10)*s2+F(4,10)*s3
    return jia,T-jia
out=[]
for T10 in range(1,5000):
    T=F(T10,10)
    j,y=split86(T)
    if y==F(12,10)*j: out.append(T)
res['M086']=[(T,split86(T),split86(T/2),split86(T/2)[0]-split86(T/2)[1]) for T in out]
# M087
best=max(((18*(2500-max(0,F(2,10)*(S-400)))+3*S),S) for S in range(0,10001))
res['M087']=best
# M088
w,p=1,1
orig=5*w*p+2*5*w*p; new=5*2*w*F(2,10)*p+2*10*w*F(5,10)*p
res['M088']=F(new)/orig
# M089
def bag(n): return 36*(n//3)+18*(n%3)
def db(n): return 36*(n//4)+12*(n%4)
out=[]
for B in range(0,57):
    D=56-B
    if bag(B)+db(D)==606: out.append((B,D,bag(B),db(D)))
res['M089']=out
# M090
best=None
for x in range(0,501):
    y=500-x; z=600-x; w_=700-z
    if min(x,y,z,w_)<0 or y+w_!=600: continue
    cost=150*x+130*y+160*z+145*w_
    if best is None or cost<best[0]: best=(cost,x,y,z,w_)
res['M090']=best
# M091
x=sp.symbols('x')
res['M091']=sp.solve(sp.Eq(x*sp.Rational(56,1000)*sp.Rational(1,2)+x/2*sp.Rational(56,1000)*sp.Rational(1,2)+(5000-x)*sp.Rational(62,1000),264),x)
# M092
res['M092']=max(x for x in range(0,101) if 200*160+100*130+(100-x)*70-40000>=10000)
# M093
sav=F(2)*F(1,10)+F(6)*F(3,10)
res['M093']=(sav,max(d for d in range(0,401) if sav*(400-d)>=600+d))
# M094
orig=20*40*36
def promo(n):
    seq=[50,60,70,80,90]+[90]*1000
    return sum(seq[:n])*16
res['M094']=(orig,min(n for n in range(1,100) if promo(n)>=orig),promo(21),promo(22))
# M095
def jia95(T):
    T=F(T); s1=min(T,10); s2=min(max(T-10,0),10); s3=max(T-20,0)
    return F(8,10)*s1+F(6,10)*s2+F(4,10)*s3
res['M095']=max(F(t,10) for t in range(1,2000) if jia95(F(t,10))>=F(t,10)/2)
# M096
v=sp.symbols('v')
vv=sp.solve(sp.Eq(120*(v+10)-100*v,2800),v)[0]
res['M096']=(vv,(vv+10)*60/1000)
for k_,v_ in res.items(): print(k_,v_)
