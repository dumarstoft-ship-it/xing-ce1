from fractions import Fraction as F
from itertools import product, combinations_with_replacement
import math

print("== Q31"); a=[F(2),F(1),F(1),F(3,2),F(3),F(15,2)]
print([a[i+1]/a[i] for i in range(5)], a[-1]*3)

print("== Q32"); a=[8,12,23,44,78]; d=[a[i+1]-a[i] for i in range(4)]; dd=[d[i+1]-d[i] for i in range(3)]; print(d,dd, 78+d[-1]+dd[-1]+3)

print("== Q33")
for s in ["1.1","3.1","6.2","5.11","30.2","21.4","56.8","63.63","124.4"]:
    i,f=s.split("."); print(s, int(i)+int(f), int(i)*int(f))

print("== Q34"); a=[180,56,146,174,247]
print([a[i+1]+a[i]/2 for i in range(len(a)-1)], 247+174/2)

print("== Q35")
seq=[F(1,2),F(2,3),F(23,28),F(58,65),F(13,14)]
for n,x in enumerate(seq,1):
    den=n**3+1; num=x*den; print(n, x, num, den, den-num)
for opt in [F(206,217),F(103,108),F(205,217),F(205,216)]: print(opt, opt*217)

print("== Q36")
for b in range(31,400):
    a_=b-30
    if abs(F(88,100)*(4*F(13,10)*a_+2*F(15,10)*b)-(4*a_+2*b)-80)<1e-9: print("cost b",b,"price B",F(15,10)*b, "price A", F(13,10)*a_)

print("== Q37")
for w in range(0,21):
    l=20-w
    if F(9,8)*w+F(4,3)*l==25: print(w,l,abs(w-l))

print("== Q38")
for m in range(1,1000):
    for cnum in range(1,100):
        c=F(cnum,100)
        if m*c/(m+20)==(m*c+15)/(m+50) and (m*c+30)/(m+50)==c: print("m",m,"c",c)

print("== Q39")
import cmath
# coordinates: x east, y north
def dirv(deg_from_north_clockwise): r=math.radians(deg_from_north_clockwise); return (math.sin(r), math.cos(r))
# B: from A bearing 60 (N60E); from D bearing 180-60=120 (S60E)
# solve A + t*u = D + s*v
import numpy as np
def inter(P,u,Q,v):
    M=np.array([[u[0],-v[0]],[u[1],-v[1]]]); rhs=np.array([Q[0]-P[0],Q[1]-P[1]]); t,s=np.linalg.solve(M,rhs); return (P[0]+t*u[0],P[1]+t*u[1])
A=(0,0); D=(0,12)
B=inter(A,dirv(60),D,dirv(120)); C=inter(A,dirv(-30),D,dirv(180+60))
print(B,C, math.dist(B,C), 6*math.sqrt(7))

print("== Q40")
# day-of-week index for July 1 = d (0=Mon..6=Sun). Interpret period p.
names=["一","二","三","四","五","六","日"]
for p in (4,5):
    for d in range(7):
        def dow(x): return (d+x-1)%7
        s1=[x for x in range(2,32,p)]; s2=[x for x in range(3,32,p)]
        sat1=sum(dow(x)==5 for x in s1); sun1=sum(dow(x)==6 for x in s1)
        sat2=sum(dow(x)==5 for x in s2); sun2=sum(dow(x)==6 for x in s2)
        if sat1==1 and sun1==1 and sat2==0 and sun2==1:
            print("period",p,"July1 = 星期"+names[d],"July31 = 星期"+names[dow(31)], s1, s2)

print("== Q41")
for L in range(24,5000,24):
    n8=L//8+1; n6=L//6+1
    # jia 7k, yi 4k per day: n8 = 11*11k, n6 = 23*7k
    if n8%121==0 and n6%161==0 and n8//121==n6//161: print("L",L,"k",n8//121)

print("== Q42")
p=F(2,5); q=F(3,5); print(3*p*p*q+p**3)
# brute force
cnt=0
for t in product(range(1,6),repeat=3):
    ev=sum(x%2==0 for x in t); cnt+= ev>3-ev
print(F(cnt,125))

print("== Q43")
best=0; arg=None
from itertools import permutations
for combo in product(range(1,40),repeat=5) if False else []: pass
# smarter: other five distinct, none equal 5 (else tie would be >3), exactly 2 above 5 (so the three 5s rank 3rd)
best=0
for x in combinations_with_replacement(range(1,40),5):
    if len(set(x))<5 or 5 in x: continue
    if sum(x)!=24: continue
    above=[v for v in x if v>5]
    if len(above)!=2: continue
    if max(x)>best: best=max(x); arg=x
print(best,arg)
# what if one ignores "并列第三" (i.e., allow any number above 5)?
best2=0
for x in combinations_with_replacement(range(1,40),5):
    if len(set(x))<5 or 5 in x or sum(x)!=24: continue
    best2=max(best2,max(x))
print("ignoring rank constraint:",best2)

print("== Q44")
ra,rb,rc=F(1,2),F(5,6),F(2,3)
T=2/(ra+rb+rc); print("T",T, "bing with yi (min)", (1-rb*T)/rc*60)

print("== Q45")
cal={'J':55,'R':80,'S':120}
def maxrun(seq):
    m=c=1
    for i in range(1,len(seq)):
        c=c+1 if seq[i]==seq[i-1] else 1; m=max(m,c)
    return m if seq else 0
ordered=[]; unordered=set()
for n in range(1,5):
    for seq in product('JRS',repeat=n):
        if sum(cal[x] for x in seq)>=360:
            ordered.append(seq); unordered.add(tuple(sorted(seq)))
print("ordered, unlimited repeats:",len(ordered))
print("unordered multisets:",len(unordered), sorted(unordered))
print("ordered, max run<=2:",sum(maxrun(s)<=2 for s in ordered))
print("ordered n=4 only:",sum(len(s)==4 for s in ordered))
print("ordered, excl. all-same seqs:",sum(len(set(s))>1 for s in ordered))
print("ordered, each item <=2 times total:",sum(max(s.count(x) for x in 'JRS')<=2 for s in ordered))
print("unordered, each item <=2 total:",sum(max(m.count(x) for x in 'JRS')<=2 for m in unordered))
print("unordered excluding all-same:",sum(len(set(m))>1 for m in unordered))
for s in ordered:
    if maxrun(s)>2: print("  run>2:", ''.join(s))
