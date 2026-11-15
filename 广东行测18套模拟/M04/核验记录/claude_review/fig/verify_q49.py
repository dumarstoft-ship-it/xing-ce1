"""Q49 check. Nets and solid are hand-read from the figure (same reading for redrawn and original;
cell-level comparison is done visually + by verify_q49_pixels.py).
Net cells: (row, col) -> pattern. Pattern types:
  ('blk', cu, cv): black quarter-square at corner (cu,cv) of the cell, cu=-1 left/+1 right, cv=-1 top/+1 bottom (net coords)
  ('out', cu, cv): outlined quarter-square at that corner
  ('tri', eu, ev): triangle whose base lies on edge (eu,ev) of the cell [(-1,0)=left edge, (0,1)=bottom edge ...], apex at centre
Folding: root cell = Front face, normal n=(0,0,1), net-right r=(1,0,0), net-down d=(0,-1,0).
"""
import numpy as np, itertools
nets = {
 1: {(1,3):('blk',1,1),(2,1):('tri',0,1),(2,2):None,(2,3):None,(2,4):('out',-1,-1),(3,4):None},
 2: {(1,2):('tri',0,-1),(2,1):('blk',1,1),(2,2):None,(2,3):None,(3,3):None,(3,4):('out',-1,1)},
 3: {(1,2):('out',-1,-1),(2,2):('blk',-1,1),(2,3):None,(2,4):('tri',0,-1),(3,1):None,(3,2):None},
 4: {(1,1):None,(1,2):None,(2,2):('tri',-1,0),(2,3):('blk',1,1),(3,3):('out',1,-1),(3,4):None},
}
def fold(net):
    cells=list(net); root=cells[0]
    frames={root:(np.array([0,0,1]),np.array([1,0,0]),np.array([0,-1,0]))}
    todo=[root]
    while todo:
        c=todo.pop(); n,r,d=frames[c]
        for (dr,dc),(nn,rr,dd) in {(0,1):(r,-n,d),(0,-1):(-r,n,d),(1,0):(d,r,-n),(-1,0):(-d,r,n)}.items():
            nb=(c[0]+dr,c[1]+dc)
            if nb in net and nb not in frames:
                frames[nb]=(nn,rr,dd); todo.append(nb)
    normals=[tuple(f[0]) for f in frames.values()]
    assert len(frames)==6 and len(set(normals))==6, 'not a cube net'
    feats=[]
    for c,p in net.items():
        if p is None: continue
        n,r,d=frames[c]; t,u,v=p
        feats.append((t,tuple(n),tuple(n+u*r+v*d)))
    return frames,feats
# Solid (x right, y up, z toward viewer). Visible faces and their single pattern (3D point = corner or base-edge midpoint)
solid = {
 'left cube':  {(0,0,1):('blk',(-1,-1,1)), (0,1,0):('out',(-1,1,1))},
 'right cube': {(0,0,1):('tri',(0,-1,1)), (0,1,0):('blk',(1,1,-1)), (1,0,0):('out',(1,1,-1))},
}
def rotations(proper=True):
    out=[]
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product([1,-1],repeat=3):
            M=np.zeros((3,3),int)
            for i,(j,s) in enumerate(zip(perm,signs)): M[i,j]=s
            if round(np.linalg.det(M))==(1 if proper else -1): out.append(M)
    return out
def matches(feats, target, Rs):
    hits=[]
    for R in Rs:
        mapped={}
        for t,n,p in feats:
            mapped.setdefault(tuple(R@np.array(n)),[]).append((t,tuple(R@np.array(p))))
        if all(mapped.get(fn,[])==[pat] for fn,pat in target.items()):
            hits.append(R)
    return hits
P=rotations(True); Mi=rotations(False)
for k,net in nets.items():
    frames,feats=fold(net)
    names={(0,0,1):'Front',(0,0,-1):'Back',(1,0,0):'Right',(-1,0,0):'Left',(0,1,0):'Top',(0,-1,0):'Bottom'}
    desc=', '.join(f'{t}@{names[n]}{p}' for t,n,p in feats)
    print(f'net {k}: folded (root=Front): {desc}')
    for cube,target in solid.items():
        h=matches(feats,target,P); hm=matches(feats,target,Mi)
        print(f'   {cube}: proper-rotation fits={len(h)}  mirror-image fits={len(hm)}')

print('\n-- where every net face lands under the fitting rotation --')
names={(0,0,1):'Front',(0,0,-1):'Back',(1,0,0):'Right',(-1,0,0):'Left',(0,1,0):'Top',(0,-1,0):'Bottom'}
for k,cube in ((2,'left cube'),(4,'right cube'),(1,'right cube')):
    frames,feats=fold(nets[k])
    Rs = matches(feats,solid[cube],P) or matches(feats,solid[cube],Mi)
    R=Rs[0]
    print(f'net {k} -> {cube}' + ('' if matches(feats,solid[cube],P) else ' (ONLY as mirror image)'))
    for c,(n,r,d) in frames.items():
        print('   cell',c,'pattern',nets[k][c],'->',names[tuple(R@n)])
