import sys
sys.path.insert(0, '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad')
import engine
from fractions import Fraction as F
def nd(label, nums, dens, opts, scales=(1,2,3)):
    print('=====',label)
    for part,seq0,idx in (('num',nums,0),('den',dens,1)):
        seq=[F(x) for x in seq0]+[None]
        for k_s in scales:
            o={k+('x%d'%k_s if k_s>1 else ''):F(v[idx]*k_s) for k,v in opts.items()}
            res,_=engine.search(seq,o,[],min_strength=1,verbose=False,show_outside=False)
            for k in o:
                lst=sorted(res[k])
                if lst: print('  %s %s=%s : %d rules e.g. %s'%(part,k,o[k],len(lst),[n for _,_,n in lst[:4]]))
nd('G4-12', [3,5,7,11,13],[2,3,5,8,13], {'A':(17,18),'B':(17,21),'C':(19,21),'D':(21,17)})
nd('G4-30', [1,2,5,13],[2,5,13,34], {'A':(21,55),'B':(34,55),'C':(34,89),'D':(55,89)})
nd('G4-03 as written', [6,4,3,2],[6,6,6,5], {'A':(1,3),'B':(1,2),'C':(2,5),'D':(1,6)})
nd('G4-03 reduced', [1,2,1,2],[1,3,2,5], {'A':(1,3),'B':(1,2),'C':(2,5),'D':(1,6)})
nd('G4-03 n/T(n)', [1,2,3,4],[1,3,6,10], {'A':(1,3),'B':(1,2),'C':(2,5),'D':(1,6)}, scales=(1,2,3,4,5,6))
nd('G4-24 as written (2/1,2/1,3/1,8/3,15/4)', [2,2,3,8,15],[1,1,1,3,4], {'A':(16,5),'B':(5,2),'C':(13,4),'D':(4,1)})
