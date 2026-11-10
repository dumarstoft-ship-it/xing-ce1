import sys
sys.path.insert(0,'/home/user/work/out2/PD2A/tools')
from rq import render
A='/home/user/work/out3/PD3A/assets'
keys=sys.argv[1:]
for k in keys:
    tag,q=k.rsplit('-',1)
    try: print(render(tag,int(q),f'{A}/{tag.replace("_xc","")}-{q}.png',250))
    except Exception as e: print(k,'ERR',e)
