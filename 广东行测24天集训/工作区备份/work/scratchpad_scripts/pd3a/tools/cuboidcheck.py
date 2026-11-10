import sys, numpy as np
sys.path.insert(0,'/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pd3a/tools')
from boxfold import fold
def cube_colors(fr, cells):
    col={}; ok=True
    for k,(c,n,u,v) in fr.items():
        cube=tuple(int(np.floor(x)) for x in (np.array(c)-0.5*np.array(n)))
        if cube in col and col[cube]!=cells[k]: ok=False
        col[cube]=cells[k]
    return ok, col
def check(cells, dims, target_gray, verbose=False):
    net=set(cells)
    res=fold(net,dims)
    matches=[]; consistent=0
    for fr in res:
        ok,col=cube_colors(fr,cells)
        if not ok: continue
        consistent+=1
        gray={k for k,v in col.items() if v=='G'}
        if gray==set(target_gray): matches.append(fr)
    return len(res), consistent, len(matches)
