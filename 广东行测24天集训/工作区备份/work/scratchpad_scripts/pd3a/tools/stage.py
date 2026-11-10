import sys
sys.path.insert(0,'/home/user/work/out2/PD2A/tools')
from rq import render
S='/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pd3a/stage'
dpi=int(sys.argv[1]); keep='--keep-opts' in sys.argv
for k in [x for x in sys.argv[2:] if not x.startswith('--')]:
    tag,q=k.rsplit('-',1)
    try: print(render(tag,int(q),f'{S}/{k}.png',dpi,keep_opts=keep))
    except Exception as e: print(k,'ERR',e)
