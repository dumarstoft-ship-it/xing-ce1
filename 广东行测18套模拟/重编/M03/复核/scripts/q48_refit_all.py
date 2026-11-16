import sys, itertools
sys.path.insert(0,'/home/user/xing-ce1/广东行测18套模拟/重编/M03/复核/scripts')
import q48_options_fit as Q
from q48_refit import refit
from q48_hidden_variants import variants
res={}
for L in 'ABCD':
    out=[]
    for i,M in enumerate(Q.ROT):
        S=Q.transform(Q.main,M)
        f,p,rc=Q.fit_option(S,L)[:3]
        out.append((f,'R%d'%i,()))
    out.sort(reverse=True)
    # refine top 3 with hidden variants
    best=[]
    for f,name,_ in out[:3]:
        i=int(name[1:])
        for sub in variants:
            S=Q.transform(Q.main+list(sub),Q.ROT[i])
            best.append((round(refit(S,L)[0],4),name,tuple(sub)))
    best.sort(reverse=True)
    print(L, best[:4])
