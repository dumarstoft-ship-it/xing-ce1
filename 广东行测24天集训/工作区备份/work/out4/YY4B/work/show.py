import json,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from qx import get, raw
from clean2 import clean_pd
for key in sys.argv[1:]:
    tag,q=key.rsplit('-',1)
    r=raw(get(tag,int(q)))
    try:
        st,o=clean_pd(r)
        print(f'== {key}'); print(st); print('  '+' | '.join(f'{k}:{v}' for k,v in o.items()))
    except Exception as e:
        print('==',key,'ERR',e); print(r)
