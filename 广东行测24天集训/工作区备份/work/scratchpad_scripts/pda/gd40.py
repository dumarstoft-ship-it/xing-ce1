from net import *
# target cube: diagonals: front (y=0) TL-BR: (0,0,1)-(1,0,0); top (z=1): front-left (0,0,1) - back-right (1,1,1); right (x=1): back-top (1,1,1) - front-bottom (1,0,0)
T={(0,-1,0):{('diag',frozenset([(0,0,1),(1,0,0)]))},(0,0,1):{('diag',frozenset([(0,0,1),(1,1,1)]))},(1,0,0):{('diag',frozenset([(1,1,1),(1,0,0)]))},
   (0,1,0):set(),(-1,0,0):set(),(0,0,-1):set()}
# local corner names: (0,0)=BL,(1,0)=BR,(1,1)=TR,(0,1)=TL ; '/'=BL-TR ; '\\'=TL-BR
S='/'; B='\\'
def sq(m): return [] if m is None else [('diag',(0,0),(1,1))] if m=='/' else [('diag',(0,1),(1,0))]
import sys
nets={}
# A: row (cols0..3) at row1: [None, '/', '/', None]? fill below after reading
nets['A']={(0,1):sq(None),(1,1):sq('/'),(2,1):sq(None),(3,1):sq(None),(2,2):sq('/'),(2,0):sq('/')}
nets['B']={(0,2):sq('\\'),(0,1):sq(None),(1,1):sq('\\'),(2,1):sq('/'),(3,1):sq(None),(3,0):sq(None)}
nets['C']={(1,2):sq(None),(0,1):sq('\\'),(1,1):sq(None),(2,1):sq(None),(3,1):sq('/'),(3,0):sq('\\')}
nets['D']={(2,2):sq('\\'),(0,1):sq('/'),(1,1):sq(None),(2,1):sq(None),(3,1):sq('\\'),(1,0):sq(None)}
for k,v in nets.items():
    try:
        f=fold(v); print(k, same(f,T))
    except Exception as e: print(k,'ERR',e)
