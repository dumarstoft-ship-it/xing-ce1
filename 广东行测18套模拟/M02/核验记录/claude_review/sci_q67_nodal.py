import numpy as np, random
# Nodes: L (battery -, ground), M (slider/S3 right/R1 left), T (rheostat right end/R2 left), S2L (R2 right/S2 pivot), Rt (right rail, ammeter top)
# Battery+ammeter+S1: ideal source U between Rt and L (S1 closed always).
def current(U,R1,R2,RP,x,S2,S3,junction):
    Ra=RP*x; Rb=RP*(1-x)          # x = fraction of rheostat left of slider
    nodes=['M','T','S2L','Rt']    # L is ground
    idx={n:i for i,n in enumerate(nodes)}
    G=np.zeros((4,4)); I=np.zeros(4)
    def res(a,b,R):
        g=1/R
        for p,q in ((a,b),(b,a)):
            if p!='L':
                G[idx[p],idx[p]]+=g
                if q!='L': G[idx[p],idx[q]]-=g
    eps=1e-9; big=1e12
    res('L','M',max(Ra,eps))
    res('M','T',eps if junction else max(Rb,eps))   # junction: slider wire also touches rheostat right end -> Rb shorted
    res('T','S2L',R2)
    res('S2L','Rt',eps if S2 else big)
    res('L','M',eps if S3 else big)
    res('M','Rt',R1)
    # voltage source at Rt: replace Rt row with V(Rt)=U
    G[idx['Rt'],:]=0; G[idx['Rt'],idx['Rt']]=1; I[idx['Rt']]=U
    V=np.linalg.solve(G,I)
    # source current = current leaving Rt into network
    Vrt=V[idx['Rt']]; Vm=V[idx['M']]; Vs=V[idx['S2L']]
    return (Vrt-Vm)/R1 + (Vrt-Vs)/(eps if S2 else big)
random.seed(1); bad={'A':0,'B':0,'C':0,'D':0}; n=0
for junction in (True,False):
    for _ in range(2000):
        U=random.uniform(1,12); R1=random.uniform(1,50)
        R2=R1 if random.random()<0.5 else random.uniform(1,50)   # stem says R1=R2; also test unequal
        RP=random.uniform(1,100); x=random.uniform(0.05,0.9); dx=random.uniform(0.01,0.09)
        I0=current(U,R1,R2,RP,x,False,False,junction)
        A=current(U,R1,R2,RP,x+dx,False,False,junction)>I0
        B=current(U,R1,R2,RP,x,True,False,junction)>I0
        C=current(U,R1,R2,RP,x,False,True,junction)>I0
        D=current(U,R1,R2,RP,x,True,True,junction)>I0
        n+=1
        bad['A']+=A; bad['B']+=not B; bad['C']+=not C; bad['D']+=not D
    print('junction' if junction else 'no-junction', 'counts of exceptions so far:',bad)
# sanity: closed-form check for junction case at slider middle, R1=R2=R
U,R,RP=6,10,20; x=0.5
print('junction, middle: I0=%.4f expected %.4f'%(current(U,R,R,RP,x,False,False,True),U/(RP/2+R)))
print('junction, S2: %.4f expected %.4f'%(current(U,R,R,RP,x,True,False,True),U/(RP/2+R/2)))
print('no-junction, S2: %.4f expected %.4f'%(current(U,R,R,RP,x,True,False,False),U/(RP/2+1/(1/R+1/(RP/2+R)))))
# sequential reading of options (A then B then C then D cumulative) for contrast
I_prev=current(U,R,R,RP,0.5,False,False,True); I_A=current(U,R,R,RP,0.6,False,False,True)
I_B=current(U,R,R,RP,0.6,True,False,True); I_C=current(U,R,R,RP,0.6,True,True,True); I_D=I_C
print('cumulative reading: A up?',I_A>I_prev,' B up?',I_B>I_A,' C up?',I_C>I_B,' D up?',I_D>I_C,'(D unchanged -> 2 false statements)')
