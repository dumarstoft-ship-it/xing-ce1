import sys
sys.path.insert(0,'/home/user/work/out2/PD2A/tools')
from rq import render
S='/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pd3a/r'
dpi=int(sys.argv[1])
for k in sys.argv[2:]:
    tag,q=k.rsplit('-',1)
    try: print(render(tag,int(q),f'{S}/{k}.png',dpi,keep_opts=True))
    except Exception as e: print(k,'ERR',e)
