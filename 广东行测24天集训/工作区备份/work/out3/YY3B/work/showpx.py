import json,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from qx import get, raw
from clean2 import clean_px
for key in sys.argv[1:]:
    tag,q=key.rsplit('-',1)
    r=raw(get(tag,int(q)))
    try:
        s,p,lead,o=clean_px(r)
        print(f'== {key}  n={len(s)} lead={lead!r}'); print('\n'.join(s)); print(p); print('  ',o)
    except Exception as e:
        print('==',key,'ERR',e); print(r)
