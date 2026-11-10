import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from matspec import MATS
from render2 import render_material
IDX='/home/user/work/index'
out='/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl4b/matprev'
os.makedirs(out, exist_ok=True)
for mid in (sys.argv[1:] or MATS):
    s=MATS[mid]; f=json.load(open(f"{IDX}/{s['tag']}.json"))[0]['file']
    im, txt = render_material(f, s['segs'], dpi=200)
    im.save(f'{out}/{mid}.png'); print(mid, im.size)
    open(f'{out}/{mid}.txt','w').write(txt)
