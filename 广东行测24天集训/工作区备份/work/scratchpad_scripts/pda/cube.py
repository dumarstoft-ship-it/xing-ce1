import itertools, numpy as np
# rotations: 24 proper rotation matrices
def rots():
    R=[]
    for p in itertools.permutations(range(3)):
        for s in itertools.product([1,-1],repeat=3):
            M=np.zeros((3,3),int)
            for i in range(3): M[i,p[i]]=s[i]
            if round(np.linalg.det(M))==1: R.append(M)
    return R
FACES={'L':(0,0),'R':(0,1),'F':(1,0),'K':(1,1),'D':(2,0),'U':(2,1)}  # axis, value ; K=back, D=bottom, U=top
def face_of_points(pts):
    for ax in range(3):
        vals={p[ax] for p in pts}
        if len(vals)==1: return ax, vals.pop()
def rotp(M,p):
    v=np.array(p)*2-1; w=M@v; return tuple(int((c+1)//2) for c in w)
def describe(pattern, M):
    """pattern: dict facename -> dict(diag=(p1,p2) or None, black=p or None, label=str)"""
    out={}
    for fn,pat in pattern.items():
        ax,val=FACES[fn]
        # rotated face location
        corners=[p for p in itertools.product([0,1],repeat=3) if p[ax]==val]
        rc=[rotp(M,p) for p in corners]
        rax,rval=face_of_points(rc)
        view={(1,0):'front',(2,1):'top',(0,1):'right'}.get((rax,rval))
        if not view: continue
        def name(p):
            q=rotp(M,p)
            if view=='front': return {(0,1):'TL',(1,1):'TR',(0,0):'BL',(1,0):'BR'}[(q[0],q[2])]
            if view=='top': return {(0,0):'FL',(1,0):'FR',(0,1):'BL',(1,1):'BR'}[(q[0],q[1])]
            if view=='right': return {(0,1):'FT',(0,0):'FB',(1,1):'BT',(1,0):'BB'}[(q[1],q[2])]
        d=pat.get('diag'); b=pat.get('black')
        desc={'face':fn}
        if d: desc['diag']='-'.join(sorted([name(d[0]),name(d[1])]))
        if b: desc['black']=name(b)
        if 'label' in pat: desc['label']=pat['label']
        out[view]=desc
    return out
