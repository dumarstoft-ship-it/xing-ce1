import sys, itertools
sys.path.insert(0, '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad')
import engine
from fractions import Fraction as F
G=[(3,4,5),(6,6,12),(12,8,28),(21,24,51)]
O={'A':(33,48,63),'B':(27,32,85),'C':(36,48,108),'D':(33,64,95)}
derived={
 'a':lambda g:g[0],'b':lambda g:g[1],'c':lambda g:g[2],
 'a+b+c':lambda g:sum(g),'a+b':lambda g:g[0]+g[1],'b+c':lambda g:g[1]+g[2],'a+c':lambda g:g[0]+g[2],
 'c-a':lambda g:g[2]-g[0],'c-b':lambda g:g[2]-g[1],'b-a':lambda g:g[1]-g[0],
 'abc':lambda g:g[0]*g[1]*g[2],'ab':lambda g:g[0]*g[1],'c-a-b':lambda g:g[2]-g[0]-g[1],
 'c/a':lambda g:F(g[2],g[0]),'b/a':lambda g:F(g[1],g[0]),'c/b':lambda g:F(g[2],g[1]),
 '3a-b-c':lambda g:3*g[0]-g[1]-g[2],'2a+b-c':lambda g:2*g[0]+g[1]-g[2],
}
for nm,f in derived.items():
    seq=[F(f(g)) for g in G]+[None]
    opts={k:F(f(v)) for k,v in O.items()}
    print('##',nm,[str(x) for x in seq[:-1]],{k:str(v) for k,v in opts.items()})
    res,out=engine.search(seq,opts,[],min_strength=1,verbose=False,show_outside=False)
    for k in O:
        lst=sorted(res[k])
        if lst: print('   ',k,len(lst),[n for _,_,n in lst[:6]])
