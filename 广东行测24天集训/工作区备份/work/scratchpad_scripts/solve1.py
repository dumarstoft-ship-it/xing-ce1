from fractions import Fraction as F
from itertools import product
import math

res = {}
# M061: a+b=c+d (monthly outputs prop to eff), a=b+240, d=c+160 -> b-c
# 2b+240 = 2c+160 -> b-c=-40
res['M061'] = ('b-c', -40)

# M062
for d1 in range(0,2000):
    d3 = d1-200
    if d3<0: continue
    tot = d1+600+d3
    if F(d1,5)==F(tot,18):
        res['M062']=(d1,tot)
# M063
for a in [F(x,2) for x in range(0,100)]:
    b=a/F(3,2); c=a-6
    if a+b+c+24==50:
        res['M063']=(a,b,c,'starts', 12-a/2, 12-b/2, 12-c/2)
# M064
# solve via enumeration of averages (rational)
# 12a - S = 8(a+3); 20b+S = 24(b+1)
import sympy as sp
a,b,S=sp.symbols('a b S')
sol=sp.solve([12*a-S-8*(a+3),20*b+S-24*(b+1)],[S,b],dict=True)
res['M064']=sp.simplify(a-sol[0][b])
# M065
x=sp.symbols('x')
xs=sp.solve(sp.Eq((100-x)-(100-sp.Rational(12,10)*x),15),x)
res['M065']=(xs, xs[0]+sp.Rational(12,10)*xs[0]-100)
# M066
out=[]
for c in range(1,400):
    z=F(16,10)*c; l=F(8,10)*(z+c)
    if z.denominator==1 and l.denominator==1:
        tot=l+z+c
        if 300<=tot<=399:
            out.append((c,z,l,tot,(-tot)%7))
res['M066']=out
# M067
out=[]
for A in range(1,400):
    inv=F(27,100)*A
    if inv.denominator!=1: continue
    for B in range(21,400,21):
        if not (300<=A+B<=399): continue
        if not B<A: continue
        bi=B//21*8
        if not bi>inv: continue
        nonA=A-inv; nonB=B-bi
        out.append((A,B,inv,bi,nonA+nonB))
res['M067']=sorted(out,key=lambda t:t[-1])[:3]
# M068
tot=369+412
out=[]
for s in range(1,tot+1):
    if tot%s: continue
    n=tot//s
    if n<2: continue
    r=369%s
    if r==0: continue
    out.append((n,s,r,s-r))
res['M068']=sorted(out)[:3]
# M069
best=None
for a_ in range(1,100):
    for b_ in range(1,a_):
        for c_ in range(1,b_):
            if a_+b_+c_==a_+10 and a_-b_>b_-c_:
                if best is None or a_<best[0]: best=(a_,b_,c_)
res['M069']=best
# M070
out=[]
B=24
for A in range(0,72):
    C=A+6; D=72-B-A-C
    if D<0: continue
    if D<A and D<B and D<C:
        out.append((A,B,C,D))
res['M070']=min(out,key=lambda t:t[2])
# M071
jia=35*12; yi=jia+10; per=F(yi,10); total=jia+yi
res['M071']=(per,total,total%per)
# M072
out=[]
for n in range(1,60):
    p1=6+2*(n-1)
    rev=sum(10*(p1-2*k) for k in range(n))
    cost=12*10*n
    if rev==2*cost: out.append((n,p1,10*n))
res['M072']=out
# M073
x=sp.symbols('x')
res['M073']=sp.solve(sp.Eq(120*1+60*sp.Rational(8,10)+180*x,360*sp.Rational(11,10)),x)
# M074
a,b,c=sp.symbols('a b c',positive=True)
s=sp.solve([2*b-(a+c),3*(a+b)+7*(b+c)-7*(a+b+c)],[b,c],dict=True)[0]
W=10*s[c]
res['M074']=(s, sp.nsimplify(W/(a+s[b])), float(W/(a+s[b])))
# M075
total=80*30*10
done=80*(30-8-10)*10
rem=total-done
res['M075']=(rem, F(rem,150*8), F(rem,150*8)-10)
# M076
k,x=sp.symbols('k x',positive=True)
xs=sp.solve(sp.Eq((5*k+x)*5,(9*k+x)*3),x)[0]
res['M076']=sp.simplify(3*xs/(24*k))
# M077
a,b=sp.symbols('a b')
T=10*a
s=sp.solve([12*b+2*a-T,15*(b-4)+2*a-T],[a,b])
res['M077']=s
# M078
x,y=sp.symbols('x y')
s=sp.solve([8*x+8*y-3,2*x+3*y-1],[x,y])
res['M078']=(s, sp.Rational(62)/(11*s[x]+10*s[y]))
# M079
out=[]
for N in range(1,200):
    if (7*N)%10 or (3*N)%10 or N%5: continue
    G=N//5; U=N-G; M=7*N//10; Fm=N-M
    for fg in range(0,G+1):
        mu=4*fg; mg=G-fg; fu=U-mu
        if mu<0 or fu<0 or mg<0: continue
        if mu+mg==M and fg+fu==Fm:
            out.append((N,fu-mg,(mu,mg,fu,fg)))
res['M079']=out[:3]
# M080
out=[]
for N in range(1,500):
    A=F(60,100)*N; Bv=F(45,100)*N
    if A.denominator!=1 or Bv.denominator!=1: continue
    for both in range(0,int(min(A,Bv))+1):
        nei=both-2
        if nei<0: continue
        if A+Bv-both+nei==N:
            out.append((N,both,nei,A+Bv-2*both))
res['M080']=max(out,key=lambda t:t[-1])
for k_,v in res.items(): print(k_,v)
