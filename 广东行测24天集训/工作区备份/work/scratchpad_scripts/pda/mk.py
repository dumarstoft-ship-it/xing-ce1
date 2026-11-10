# usage: mk.py tag qno [tag qno ...] -> assets/<tag>-<qno>.png at 200dpi (env DPI overrides)
import sys, os
from importlib import util
spec=util.spec_from_file_location('asset','/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pda/asset.py'); m=util.module_from_spec(spec); spec.loader.exec_module(m)
OUT='/home/user/work/out/PD-A/assets'
a=sys.argv[1:]; dpi=int(os.environ.get('DPI','200'))
for i in range(0,len(a),2):
    tag,q=a[i],int(a[i+1]); im=m.render(tag,q,dpi); p=f"{OUT}/{tag.replace('_xc','')}-{q}.png"; im.save(p); print(p, im.size)
