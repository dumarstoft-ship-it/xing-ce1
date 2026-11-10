import sys
sys.path.insert(0, '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad')
import engine
from fractions import Fraction as F
N=[1123,2436,3547,4759]
O={'A':6880,'B':5879,'C':5970,'D':7327}
def dg(n): return [int(ch) for ch in '%04d'%n]
derived={
 'd1':lambda n:dg(n)[0],'d2':lambda n:dg(n)[1],'d3':lambda n:dg(n)[2],'d4':lambda n:dg(n)[3],
 'ab':lambda n:n//100,'cd':lambda n:n%100,'cd-ab':lambda n:n%100-n//100,'ab+cd':lambda n:n%100+n//100,
 'abc':lambda n:n//10,'bcd':lambda n:n%1000,'digitsum':lambda n:sum(dg(n)),
 'ac':lambda n:dg(n)[0]*10+dg(n)[2],'bd':lambda n:dg(n)[1]*10+dg(n)[3],
 'a+b':lambda n:dg(n)[0]+dg(n)[1],'c+d':lambda n:dg(n)[2]+dg(n)[3],'a*b':lambda n:dg(n)[0]*dg(n)[1],'c*d':lambda n:dg(n)[2]*dg(n)[3],
 'ab*cd':lambda n:(n//100)*(n%100),'digprod':lambda n:dg(n)[0]*dg(n)[1]*dg(n)[2]*dg(n)[3],
 'whole':lambda n:n,'d-b':lambda n:dg(n)[3]-dg(n)[1],'c-a':lambda n:dg(n)[2]-dg(n)[0],
 'reverse':lambda n:int(('%04d'%n)[::-1]),'b+c':lambda n:dg(n)[1]+dg(n)[2],'a+d':lambda n:dg(n)[0]+dg(n)[3],
 'a+c':lambda n:dg(n)[0]+dg(n)[2],'b+d':lambda n:dg(n)[1]+dg(n)[3],
 'a+b+c-d':lambda n:dg(n)[0]+dg(n)[1]+dg(n)[2]-dg(n)[3],
}
for nm,f in derived.items():
    seq=[F(f(x)) for x in N]+[None]
    opts={k:F(f(v)) for k,v in O.items()}
    res,out=engine.search(seq,opts,[],min_strength=1,verbose=False,show_outside=False)
    line='## %-9s %s  opts %s'%(nm,[int(x) for x in seq[:-1]],{k:int(v) for k,v in opts.items()})
    print(line)
    for k in O:
        lst=sorted(res[k])
        if lst: print('     ',k,len(lst),[n for _,_,n in lst[:5]])
