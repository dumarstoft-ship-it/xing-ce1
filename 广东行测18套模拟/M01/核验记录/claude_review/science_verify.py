import random, itertools
print("== Q67 circuit (ideal source U, ideal meters; V across R1+R2 branch = U)")
def meters(U,R1,R2,R3,R4):
    I12=U/(R1+R2); R34=R3*R4/(R3+R4); I34=U/R34
    return dict(V=U, A1=I12+I34, A2=I34)
random.seed(1)
res={'A':0,'B':0,'C':0,'D':0}; N=2000
for _ in range(N):
    U=random.uniform(1,20); R1,R2,R3,R4=[random.uniform(1,100) for _ in range(4)]
    base=meters(U,R1,R2,R3,R4)
    tdown=meters(U,R1,R2*0.8,R3,R4)   # temp down -> R2 smaller
    lup=meters(U,R1,R2,R3*0.8,R4)     # light up -> R3 smaller
    ldown=meters(U,R1,R2,R3*1.25,R4)  # light down -> R3 larger
    res['A']+= tdown['V']<base['V'] and tdown['A1']>base['A1']
    res['B']+= tdown['V']==base['V'] and tdown['A1']>base['A1']
    res['C']+= lup['A1']>base['A1'] and lup['A2']<base['A2']
    res['D']+= abs(ldown['A1']-base['A1'])<1e-12 and ldown['A2']>base['A2']
print({k:f"{v}/{N}" for k,v in res.items()})
# non-ideal: internal resistance r>0 -> does any other option become true?
res2={'A':0,'B':0,'C':0,'D':0}
for _ in range(N):
    U=random.uniform(1,20); r=random.uniform(0.1,20); R1,R2,R3,R4=[random.uniform(1,100) for _ in range(4)]
    def m(R1,R2,R3,R4):
        R12=R1+R2; R34=R3*R4/(R3+R4); Rp=R12*R34/(R12+R34); I=U/(r+Rp); Vp=I*Rp
        return dict(V=Vp,A1=I,A2=Vp/R34)
    base=m(R1,R2,R3,R4); td=m(R1,R2*0.8,R3,R4); lu=m(R1,R2,R3*0.8,R4); ld=m(R1,R2,R3*1.25,R4)
    res2['A']+= td['V']<base['V'] and td['A1']>base['A1']
    res2['B']+= abs(td['V']-base['V'])<1e-12 and td['A1']>base['A1']
    res2['C']+= lu['A1']>base['A1'] and lu['A2']<base['A2']
    res2['D']+= abs(ld['A1']-base['A1'])<1e-12 and ld['A2']>base['A2']
print("with internal resistance (NOT the stated model):",{k:f"{v}/{N}" for k,v in res2.items()})

print("== Q68 metals")
facts={1:{('Fe','Cu')},2:{('Cu','Ag')},3:{('Cu','Ag')},4:{('Fe','Cu')}}
def total(order_pairs):
    # need Fe>Cu and Cu>Ag
    return ('Fe','Cu') in order_pairs and ('Cu','Ag') in order_pairs
for name,combo in {'A':(1,3),'B':(1,4),'C':(2,4),'D':(3,4)}.items():
    s=set().union(*[facts[i] for i in combo]); print(name,combo,"can" if total(s) else "CANNOT")

print("== Q69 ABO")
geno={'A':[('A','A'),('A','O')],'B':[('B','B'),('B','O')],'AB':[('A','B')],'O':[('O','O')]}
def pheno(a,b):
    s={a,b}
    if s=={'A','B'}: return 'AB'
    if 'A' in s: return 'A'
    if 'B' in s: return 'B'
    return 'O'
def kids(p1,p2):
    out=set()
    for g1 in geno[p1]:
        for g2 in geno[p2]:
            for a in g1:
                for b in g2: out.add(pheno(a,b))
    return out
print("A x B ->",sorted(kids('A','B')))
print("O child possible from parents:",[(x,y) for x in geno for y in geno if x<=y and 'O' in kids(x,y)])
print("AB x O ->",sorted(kids('AB','O')))
print("AB child possible from parents:",[(x,y) for x in geno for y in geno if x<=y and 'AB' in kids(x,y)])
