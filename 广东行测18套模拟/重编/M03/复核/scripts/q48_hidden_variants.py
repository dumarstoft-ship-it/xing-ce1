# Try main object plus hidden-cube additions (cubes invisible in the main view) against options A and D
import sys, itertools
sys.path.insert(0,'/home/user/xing-ce1/广东行测18套模拟/重编/M03/复核/scripts')
from q48_options_fit import main, ROT, MIR, transform, fit_option
hidden=[(-1,3,-1),(-1,3,0),(-1,3,1),(-1,4,-1),(0,2,0),(0,3,0),(0,4,-1),(0,4,0),(1,2,0),(1,2,1),(1,3,0),(1,3,1),(2,3,0)]
def connected_with(S):
    S=set(S); start=next(iter(S)); seen={start}; st=[start]
    while st:
        v=st.pop()
        for dlt in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
            w=(v[0]+dlt[0],v[1]+dlt[1],v[2]+dlt[2])
            if w in S and w not in seen: seen.add(w); st.append(w)
    return len(seen)==len(S)
variants=[[]]
for k in (1,2,3):
    for sub in itertools.combinations(hidden,k):
        if connected_with(main+list(sub)): variants.append(list(sub))
print('variants',len(variants))
for L in 'AD':
    best=[]
    for sub in variants:
        for i,M in enumerate(ROT):
            S=transform(main+sub,M)
            f,p,rc,ox,oy,_=fit_option(S,L)
            best.append((round(f,3),'R%d'%i,tuple(sub)))
    best.sort(reverse=True)
    print(L,best[:6])
