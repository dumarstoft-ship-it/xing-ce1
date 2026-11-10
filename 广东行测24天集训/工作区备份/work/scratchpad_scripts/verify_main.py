from fractions import Fraction as F
import math

def chk(name, cond):
    print(("OK  " if cond else "FAIL") + " " + name)

def primes(n):
    out=[];k=2
    while len(out)<n:
        if all(k%p for p in out if p*p<=k): out.append(k)
        k+=1
    return out

print("=== G4-01: a(n)-a(n+2)=2n-1 ; also a(n)+a(n+1)=8-(n-1)^2")
opts={'A':-5,'B':-7,'C':-9,'D':-11}
for k,v in opts.items():
    s=[3,5,2,2,-3,v,-12]
    r1=all(s[i]-s[i+2]==2*(i+1)-1 for i in range(5))
    r2=all(s[i]+s[i+1]==8-i*i for i in range(6))
    d=[s[i+1]-s[i] for i in range(6)]
    print(k,v,"rule1",r1,"rule2",r2,"diffs",d)

print("=== G4-02: odd n^2+2, even -(n^2+n+3)")
opts={'A':-33,'B':27,'C':35,'D':45}
for k,v in opts.items():
    s=[3,-5,6,-9,11,-15,18,-23,v]
    odd=s[0::2]; ev=s[1::2]
    r=all(odd[i]==(i+1)**2+2 for i in range(len(odd))) and all(ev[i]==-((i+1)**2+(i+1)+3) for i in range(len(ev)))
    a=[abs(x) for x in s]; d=[a[i+1]-a[i] for i in range(8)]
    print(k,v,r,"abs diffs",d)

print("=== G4-03: value 2/(n+1)")
opts={'A':F(1,3),'B':F(1,2),'C':F(2,5),'D':F(1,6)}
for k,v in opts.items():
    s=[F(6,6),F(4,6),F(3,6),F(2,5),v]
    print(k,v,all(s[i]==F(2,i+2) for i in range(5)))

print("=== G4-04: 2nd diffs primes")
opts={'A':103,'B':109,'C':116,'D':122}
for k,v in opts.items():
    s=[-7,1,11,24,42,67,v]
    d=[s[i+1]-s[i] for i in range(6)]; d2=[d[i+1]-d[i] for i in range(5)]
    print(k,v,d,d2, d2==primes(5))

print("=== G4-05: a(n+2)=a(n)-a(n+1)/2")
opts={'A':3,'B':9,'C':17,'D':24}
for k,v in opts.items():
    s=[F(36),F(24),F(24),F(12),F(18),F(v),F(33,2)]
    print(k,v,all(s[i+2]==s[i]-s[i+1]/2 for i in range(5)))

print("=== G4-06: radicand 2^(n+1)+3")
opts={'A':99,'B':123,'C':131,'D':135}
for k,v in opts.items():
    s=[7,11,19,35,67,v]
    print(k,v,all(s[i]==2**(i+2)+3 for i in range(6)))

print("=== G4-08: a(n)=a(n-1)+a(n-2)-(n-3)")
opts={'A':28,'B':29,'C':30,'D':31}
for k,v in opts.items():
    s=[2,4,6,9,13,19,v]
    r=all(s[i]==s[i-1]+s[i-2]-(i-2) for i in range(2,7))
    d=[s[i+1]-s[i] for i in range(6)]; d2=[d[i+1]-d[i] for i in range(5)]
    print(k,v,r,d,d2)

print("=== G4-09: n^(n-1)")
opts={'A':981,'B':1296,'C':7776,'D':15625}
for k,v in opts.items():
    s=[1,2,9,64,625,v]
    print(k,v,all(s[i]==(i+1)**i for i in range(6)))

print("=== G4-10: a(n+2)=a(n+1)+a(n)/2")
opts={'A':61,'B':69,'C':77,'D':85}
for k,v in opts.items():
    s=[F(36),F(12),F(30),F(36),F(51),F(v),F(189,2)]
    print(k,v,all(s[i+2]==s[i+1]+s[i]/2 for i in range(5)))

print("=== G4-11: base m=n-2; odd pos m^3-1, even pos m^2+1")
opts={'A':196,'B':216,'C':278,'D':342}
for k,v in opts.items():
    s=[-2,1,0,5,26,17,124,37,v]
    r=all(s[i]==((i-1)**3-1 if i%2==0 else (i-1)**2+1) for i in range(9))
    print(k,v,r)

print("=== G4-12: num primes from 3, den Fibonacci 2,3,5,8,13,21")
opts={'A':F(17,18),'B':F(17,21),'C':F(19,21),'D':F(21,17)}
nums=[3,5,7,11,13,17]; dens=[2,3,5,8,13,21]
for k,v in opts.items():
    s=[F(3,2),F(5,3),F(7,5),F(11,8),F(1),v]
    print(k,v,all(s[i]==F(nums[i],dens[i]) for i in range(6)))

print("=== G4-13: a(n+2)=2a(n)-a(n+1)")
opts={'A':44,'B':56,'C':68,'D':80}
for k,v in opts.items():
    s=[5,2,8,-4,20,-28,v]
    d=[s[i+1]-s[i] for i in range(6)]
    print(k,v,all(s[i+2]==2*s[i]-s[i+1] for i in range(5)),d)

print("=== G4-14: (4n-2)^2-1")
opts={'A':272,'B':306,'C':323,'D':340}
for k,v in opts.items():
    s=[3,35,99,195,v]
    print(k,v,all(s[i]==(4*i+2)**2-1 for i in range(5)))

print("=== G4-15: int part primes, decimal 2^(n+1)-1")
opts={'A':'13.125','B':'17.127','C':'13.126','D':'13.127'}
P=primes(6)
for k,v in opts.items():
    s=['2.3','3.7','5.15','7.31','11.63',v]
    r=all(int(x.split('.')[0])==P[i] and int(x.split('.')[1])==2**(i+2)-1 for i,x in enumerate(s))
    print(k,v,r)

print("=== G4-16: adjacent sums consecutive primes")
opts={'A':7,'B':8,'C':9,'D':10}
for k,v in opts.items():
    s=[1,1,2,3,4,v,6]
    sm=[s[i]+s[i+1] for i in range(6)]
    print(k,v,sm, sm==primes(6))

print("=== G4-17: a(n)=2a(n-1)+a(n-2)")
opts={'A':64,'B':65,'C':66,'D':67}
for k,v in opts.items():
    s=[-9,6,3,12,27,v]
    print(k,v,all(s[i]==2*s[i-1]+s[i-2] for i in range(2,6)))

print("=== G4-18: (6-n)^(3-n)")
opts={'A':F(0),'B':F(1,4),'C':F(1,3),'D':F(1)}
for k,v in opts.items():
    s=[F(25),F(4),F(1),F(1,2),v]
    print(k,v,all(s[i]==F(5-i)**(2-i) for i in range(5)))

print("=== G4-19: diffs (n-1)!")
opts={'A':86,'B':123,'C':161,'D':192}
for k,v in opts.items():
    s=[7,8,9,11,17,41,v]
    d=[s[i+1]-s[i] for i in range(6)]
    print(k,v,d, d==[math.factorial(i) for i in range(6)])

print("=== G4-20: a(n)=n*a(n-1)+(n-1)")
opts={'A':475,'B':479,'C':483,'D':489}
for k,v in opts.items():
    s=[3,7,23,95,v,2879]
    print(k,v,all(s[i]==(i+1)*s[i-1]+i for i in range(1,6)), [x+1 for x in s])

print("=== G4-21: a(n)=3a(n-1)-a(n-2)")
opts={'A':666,'B':669,'C':696,'D':699}
for k,v in opts.items():
    s=[3,6,15,39,102,267,v]
    d=[s[i+1]-s[i] for i in range(6)]
    print(k,v,all(s[i]==3*s[i-1]-s[i-2] for i in range(2,7)),d)

print("=== G4-22: diffs -primes")
opts={'A':2,'B':6,'C':10,'D':14}
for k,v in opts.items():
    s=[42,40,37,32,25,v,1]
    d=[s[i]-s[i+1] for i in range(6)]
    print(k,v,d,d==primes(6))

print("=== G4-23: digit sums 5,5,10,10,15,15")
opts={'A':53,'B':69,'C':81,'D':93}
for k,v in opts.items():
    s=[23,14,37,55,78,v]
    ds=[sum(map(int,str(x))) for x in s]
    print(k,v,ds)

print("=== G4-24: adjacent products 4,6,8,10,12")
opts={'A':F(16,5),'B':F(5,2),'C':F(13,4),'D':F(4)}
for k,v in opts.items():
    s=[F(2),F(2),F(3),F(8,3),F(15,4),v]
    pr=[s[i]*s[i+1] for i in range(5)]
    print(k,v,[str(x) for x in pr])

print("=== G4-25: 3rd diffs const")
opts={'A':69,'B':79,'C':89,'D':99}
for k,v in opts.items():
    s=[1,5,17,43,v,161]
    d=[s[i+1]-s[i] for i in range(5)]; d2=[d[i+1]-d[i] for i in range(4)]; d3=[d2[i+1]-d2[i] for i in range(3)]
    print(k,v,d,d2,d3, all(s[i]==(i+1)**3-i*(2*i+1) for i in range(6)))

print("=== G4-27: 2nd diffs odd")
opts={'A':112,'B':113,'C':95,'D':96}
for k,v in opts.items():
    s=[21,30,40,53,71,v]
    d=[s[i+1]-s[i] for i in range(5)]; d2=[d[i+1]-d[i] for i in range(4)]
    print(k,v,d,d2)

print("=== G4-28: odd x2+1, even /3")
opts={'A':1,'B':3,'C':6,'D':9}
for k,v in opts.items():
    s=[2,81,5,27,11,9,23,v,47]
    o=s[0::2]; e=s[1::2]
    print(k,v,all(o[i+1]==2*o[i]+1 for i in range(len(o)-1)), all(F(e[i+1])==F(e[i],3) for i in range(len(e)-1)))

print("=== G4-29: adjacent sums primes 3,5,7,11,13")
opts={'A':8,'B':9,'C':12,'D':17}
for k,v in opts.items():
    s=[-2,5,0,7,4,v]
    sm=[s[i]+s[i+1] for i in range(5)]
    d=[s[i+1]-s[i] for i in range(5)]
    g2=[s[i+2]-s[i] for i in range(4)]
    print(k,v,"sums",sm,"diffs",d,"gap2",g2)

print("=== G4-30: F(2k-1)/F(2k+1)")
opts={'A':F(21,55),'B':F(34,55),'C':F(34,89),'D':F(55,89)}
fib=[1,1]
while len(fib)<20: fib.append(fib[-1]+fib[-2])
# 1,1,2,3,5,8,13,21,34,55,89
for k,v in opts.items():
    s=[F(1,2),F(2,5),F(5,13),F(13,34),v]
    print(k,v,all(s[i]==F(fib[2*i+1],fib[2*i+3]) for i in range(5)))
