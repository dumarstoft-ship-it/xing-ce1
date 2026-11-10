import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plan4 import PLAN, PXPLAN
from qx import get, raw
from clean4 import clean_pd4, clean_px4
def show(keys):
    for k in keys:
        tag,q=k.rsplit('-',1); r=raw(get(tag,int(q)))
        if any(k in PXPLAN[d] for d in PXPLAN):
            s,p,lead,o,ch=clean_px4(r); print(f'== {k} PX n={len(s)} lead={lead!r} RAD={ch}'); print('\n'.join(s)); print('>>',p); print(o)
        else:
            ps,pr,o,ch=clean_pd4(r); print(f'== {k} RAD={ch}'); print(ps); print('>>',pr); print(' | '.join(f'{L}:{v}' for L,v in o.items()))
if __name__=='__main__':
    if sys.argv[1:]: show(sys.argv[1:])
    else:
        for d in PLAN: show(PLAN[d]+PXPLAN[d])
