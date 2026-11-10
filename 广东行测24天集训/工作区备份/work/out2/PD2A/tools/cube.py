# PD2A verification helpers (render-clean / grid reading / cube-net folding / polycube rotation & exact cover / circle-fit). See report.
"""Bitmap-based cube net folding verifier.
net: dict cell(row,col)->bitmap (N x N, float darkness 0..1), sampled with image-right=u, image-down=v.
fold(net) -> dict cell -> (n,u,v) 3D frames (numpy int vectors), start cell keeps n=+z,u=+x,v=-y.
views: for cube orientation R (3x3 rotation), visible faces: front(-? ) we define cube axes after rotation:
 world: X right, Y up, Z toward viewer(front). Visible faces in standard oblique drawing: front (+Z), top (+Y), right (+X).
 screen orientation for each visible face: front: right=+X, down=-Y ; top: right=+X, down=+Z (toward viewer) ; right: right=-Z (going back), down=-Y.
"""
import numpy as np, itertools
from PIL import Image
N=20
def sample_quad(a, TL, TR, BL, n=N, margin=0.1, sub=4):
    """max-pooled darkness bitmap from image a (gray 0..255) over parallelogram TL,TR,BL."""
    TL=np.array(TL,float); TR=np.array(TR,float); BL=np.array(BL,float)
    m=n*sub; hi=np.zeros((m,m))
    for i in range(m):
        t=margin+(1-2*margin)*(i+0.5)/m
        for j in range(m):
            s=margin+(1-2*margin)*(j+0.5)/m
            p=TL+s*(TR-TL)+t*(BL-TL)
            x,y=int(round(p[0])),int(round(p[1]))
            hi[i,j]=1-a[y,x]/255
    return hi.reshape(n,sub,n,sub).max(axis=(1,3))
def fold(cells):
    cells=list(cells); start=cells[0]
    fr={start:(np.array([0,0,1]),np.array([1,0,0]),np.array([0,-1,0]))}
    todo=[start]
    while todo:
        c=todo.pop(); n,u,v=fr[c]; r,k=c
        for d,(dr,dk) in {'R':(0,1),'L':(0,-1),'D':(1,0),'U':(-1,0)}.items():
            nb=(r+dr,k+dk)
            if nb in cells and nb not in fr:
                if d=='R': f=(u,-n,v)
                elif d=='L': f=(-u,n,v)
                elif d=='D': f=(v,u,-n)
                else: f=(-v,u,n)
                fr[nb]=f; todo.append(nb)
    assert len(fr)==6, 'net not connected'
    normals=sorted(tuple(f[0]) for f in fr.values())
    assert len(set(normals))==6, 'not a valid cube net'
    return fr
def rotations():
    R=[]
    for p in itertools.permutations(range(3)):
        for s in itertools.product([1,-1],repeat=3):
            M=np.zeros((3,3),int)
            for i in range(3): M[i,p[i]]=s[i]
            if round(np.linalg.det(M))==1: R.append(M)
    return R
VIS={'front':(np.array([0,0,1]),np.array([1,0,0]),np.array([0,-1,0])),
     'top':(np.array([0,1,0]),np.array([1,0,0]),np.array([0,0,1])),
     'right':(np.array([1,0,0]),np.array([0,0,-1]),np.array([0,-1,0]))}
def face_view(bm, u, v, su, sv):
    """bitmap bm defined with local (u right, v down). Return how it looks with screen right=su, down=sv (3D vectors in face plane)."""
    # cases: su=u,sv=v identity; rotations
    if (su==u).all() and (sv==v).all(): return bm
    if (su==-v).all() and (sv==u).all(): return np.rot90(bm,-1)   # rotate cw: new right=-v? check below
    if (su==-u).all() and (sv==-v).all(): return np.rot90(bm,2)
    if (su==v).all() and (sv==-u).all(): return np.rot90(bm,1)
    raise ValueError('mirror?')
def render(net, fr, R):
    """For rotation R applied to folded cube, return dict visible-> bitmap"""
    out={}
    for name,(N_,SU,SV) in VIS.items():
        for c,(n,u,v) in fr.items():
            if (R@n==N_).all():
                out[name]=(c, face_view(net[c], R@u, R@v, SU, SV))
    return out
def score(pred, obs):
    a=(pred>0.5).astype(float); b=(obs>0.5).astype(float)
    return np.abs(a-b).mean()
def check(net, opts, verbose=True):
    fr=fold(net.keys())
    res={}
    for name,obs in opts.items():
        best=None
        for R in rotations():
            rv=render(net,fr,R)
            s=sum(score(rv[k][1],obs[k]) for k in ('front','top','right'))/3
            if best is None or s<best[0]: best=(s,[rv[k][0] for k in ('front','top','right')])
        res[name]=best
        if verbose: print(name,'best mismatch %.3f'%best[0],'faces(front,top,right)=',best[1])
    return res
from scipy import ndimage as nd
def cube_corners(mask, tol=6):
    """mask: bool array of a single cube drawing (dark pixels). returns dict of corners (x,y)."""
    sil=nd.binary_fill_holes(nd.binary_closing(mask,iterations=2))
    ys,xs=np.where(sil)
    maxy=ys.max(); miny=ys.min(); maxx=xs.max(); minx=xs.min()
    bot=xs[ys>=maxy-tol]; FBL=(bot.min(),maxy); FBR=(bot.max(),maxy)
    rgt=ys[xs>=maxx-tol]; RTB=(maxx,rgt.min()); RBB=(maxx,rgt.max())
    top=xs[ys<=miny+tol]; TBL=(top.min(),miny); TTR=(top.max(),miny)
    lft=ys[xs<=minx+tol]; FTL=(minx,lft.min()); FBL2=(minx,lft.max())
    FTR=(FBR[0],FTL[1])
    return dict(FBL=FBL,FBR=FBR,RBB=RBB,RTB=RTB,TBL=TBL,FTL=FTL,FTR=FTR,TTR=TTR)
def cube_faces(a, C, n=N, margin=0.08):
    """sample front/top/right bitmaps given corners C."""
    return {'front':sample_quad(a,C['FTL'],C['FTR'],C['FBL'],n,margin),
            'top':sample_quad(a,C['TBL'],C['RTB'],C['FTL'],n,margin),
            'right':sample_quad(a,C['FTR'],C['RTB'],C['FBR'],n,margin)}
def show_bm(bm):
    return '\n'.join(''.join('#' if x>0.5 else '.' for x in row) for row in bm)
def components(mask, minarea=2000):
    lab,n=nd.label(nd.binary_dilation(mask,iterations=3))
    out=[]
    for i in range(1,n+1):
        m=(lab==i)&mask
        if m.sum()>=minarea:
            ys,xs=np.where(m); out.append((xs.min(),ys.min(),xs.max(),ys.max(),m))
    return sorted(out,key=lambda t:t[0])
def soft(bm, sigma=1.0):
    f=nd.binary_fill_holes(bm>0.5).astype(float)  # fill hollow shapes so outlines ~ regions
    return nd.gaussian_filter(np.maximum(f,(bm>0.5).astype(float)),sigma)
def check_soft(net, opts, sigma=1.0, verbose=True, topk=3):
    fr=fold(net.keys())
    res={}
    for name,obs in opts.items():
        cands=[]
        for R in rotations():
            rv=render(net,fr,R)
            s=sum(np.abs(soft(rv[k][1],sigma)-soft(obs[k],sigma)).mean() for k in ('front','top','right'))/3
            cands.append((round(s,4),[rv[k][0] for k in ('front','top','right')]))
        cands.sort(key=lambda t:t[0])
        res[name]=cands[:topk]
        if verbose: print(name, cands[:2])
    return res
def edge_map(fr):
    """for each face cell and local edge in {'T','R','B','L'} -> neighbor cell across that edge (after folding)."""
    out={}
    for c,(n,u,v) in fr.items():
        dirs={'T':-v,'B':v,'L':-u,'R':u}
        out[c]={}
        for e,d in dirs.items():
            for c2,(n2,u2,v2) in fr.items():
                if (n2==d).all(): out[c][e]=c2
    return out
def corner_cycle(fr, faces):
    """given 3 mutually adjacent faces, return True if their order is clockwise when viewed from outside at the shared vertex."""
    ns=[fr[f][0] for f in faces]
    # vertex direction = sum of normals; viewed from outside, clockwise order <=> det(n1,n2,n3) < 0 (right-handed coords, viewer along +vertex)
    return np.linalg.det(np.array(ns))
def sample_gray(a, TL, TR, BL, n=10, margin=0.12):
    """point-sample: 1 for gray fill (60..215), 0 for white(>215), nan for black lines(<60)"""
    TL=np.array(TL,float); TR=np.array(TR,float); BL=np.array(BL,float)
    out=np.zeros((n,n))
    for i in range(n):
        t=margin+(1-2*margin)*(i+0.5)/n
        for j in range(n):
            s=margin+(1-2*margin)*(j+0.5)/n
            p=TL+s*(TR-TL)+t*(BL-TL); x,y=int(round(p[0])),int(round(p[1]))
            v=np.median(a[y-2:y+3,x-2:x+3])
            out[i,j]=np.nan if v<60 else (1.0 if v<=215 else 0.0)
    return out
def cmp_gray(p,q):
    m=~(np.isnan(p)|np.isnan(q))
    return np.abs(p[m]-q[m]).mean() if m.any() else 1.0
def check_gray(net, opts, verbose=True):
    fr=fold(net.keys()); res={}
    for name,obs in opts.items():
        c=[]
        for R in rotations():
            rv=render(net,fr,R)
            s=np.mean([cmp_gray(rv[k][1],obs[k]) for k in ('front','top','right')])
            c.append((round(float(s),3),[rv[k][0] for k in ('front','top','right')]))
        c.sort(key=lambda t:t[0]); res[name]=c[:3]
        if verbose: print(name,c[:3])
    return res
def sample_bw(a, TL, TR, BL, n=10, margin=0.12, thr=100, win=3):
    TL=np.array(TL,float); TR=np.array(TR,float); BL=np.array(BL,float)
    out=np.zeros((n,n))
    for i in range(n):
        t=margin+(1-2*margin)*(i+0.5)/n
        for j in range(n):
            s=margin+(1-2*margin)*(j+0.5)/n
            p=TL+s*(TR-TL)+t*(BL-TL); x,y=int(round(p[0])),int(round(p[1]))
            w=a[y-win:y+win+1,x-win:x+win+1]
            frac=(w<thr).mean()
            out[i,j]=1.0 if frac>0.8 else (0.0 if frac<0.2 else np.nan)
    return out
def option_cubes(a, xranges, y0, y1, sampler, n=10, margin=0.1, thr=200):
    opts={}
    for name,(x0,x1) in xranges.items():
        sub=a[y0:y1, x0:x1]
        m=sub<thr
        lab,k=nd.label(nd.binary_closing(m,iterations=2))
        sizes=nd.sum(m,lab,range(1,k+1)); i=1+int(np.argmax(sizes))
        C=cube_corners(nd.binary_fill_holes(lab==i))
        opts[name]={'front':sampler(sub,C['FTL'],C['FTR'],C['FBL'],n,margin),
                    'top':sampler(sub,C['TBL'],C['RTB'],C['FTL'],n,margin),
                    'right':sampler(sub,C['FTR'],C['RTB'],C['FBR'],n,margin)}
    return opts
def pr(bm):
    return '\n'.join(''.join('?' if np.isnan(v) else ('#' if v else '.') for v in row) for row in bm)
def sample_3(a, TL, TR, BL, n=12, margin=0.06):
    """3-class: 2=black fill, 1=line, 0=white, using local window darkness fraction"""
    TL=np.array(TL,float); TR=np.array(TR,float); BL=np.array(BL,float)
    out=np.zeros((n,n))
    for i in range(n):
        t=margin+(1-2*margin)*(i+0.5)/n
        for j in range(n):
            s=margin+(1-2*margin)*(j+0.5)/n
            p=TL+s*(TR-TL)+t*(BL-TL); x,y=int(round(p[0])),int(round(p[1]))
            w=a[y-3:y+4,x-3:x+4]; f=(w<110).mean()
            out[i,j]=2 if f>0.75 else (1 if f>0.08 else 0)
    return out
def cmp3(p,q):
    # black-fill mismatch weighted 1; line presence mismatch weighted 0.5 (dilate tolerance)
    pb=(p==2); qb=(q==2)
    pl=nd.binary_dilation(p>=1,iterations=1); ql=nd.binary_dilation(q>=1,iterations=1)
    e1=(pb!=qb).mean()
    e2=(((p>=1)&~ql).sum()+((q>=1)&~pl).sum())/max(1,((p>=1)|(q>=1)).sum())
    return e1+0.5*e2
def check3(net, opts, verbose=True):
    fr=fold(net.keys()); res={}
    for name,obs in opts.items():
        c=[]
        for R in rotations():
            rv=render(net,fr,R)
            s=np.mean([cmp3(rv[k][1],obs[k]) for k in ('front','top','right')])
            c.append((round(float(s),3),[rv[k][0] for k in ('front','top','right')]))
        c.sort(key=lambda t:t[0]); res[name]=c[:3]
        if verbose: print(name,c[:3])
    return res
def pr3(bm): return '\n'.join(''.join('#/ '[2-int(v)] if False else {2:'#',1:'+',0:'.'}[int(v)] for v in row) for row in bm)
def canon_frame(n):
    n=tuple(int(x) for x in n)
    table={(0,0,1):((1,0,0),(0,-1,0)),(0,0,-1):((-1,0,0),(0,-1,0)),(1,0,0):((0,0,-1),(0,-1,0)),(-1,0,0):((0,0,1),(0,-1,0)),
           (0,1,0):((1,0,0),(0,0,1)),(0,-1,0):((1,0,0),(0,0,-1))}
    su,sv=table[n]; return np.array(su),np.array(sv)
def decorated(net, fr, R=np.eye(3,dtype=int)):
    out={}
    for c,(n,u,v) in fr.items():
        n2,u2,v2=R@n,R@u,R@v
        su,sv=canon_frame(n2)
        out[tuple(n2)]=face_view(net[c],u2,v2,su,sv)
    return out
def same_cube(net1, net2, cmp):
    fr1=fold(net1.keys()); fr2=fold(net2.keys())
    d2=decorated(net2,fr2)
    best=None
    for R in rotations():
        d1=decorated(net1,fr1,R)
        s=np.mean([cmp(d1[k],d2[k]) for k in d2])
        if best is None or s<best: best=s
    return best
def detect_net(a, x0, y0, x1, y1, cs_guess=None, THRESH=0.85):
    """detect grid cells of a net drawn in region; returns (cells dict (r,c)->(TL,TR,BL)), cell size"""
    sub=a[y0:y1,x0:x1]<128
    ys,xs=np.where(sub); bx0,by0,bx1,by1=xs.min(),ys.min(),xs.max(),ys.max()
    # find vertical line positions: columns with long dark runs
    def runs_long(v, L):
        best=cur=0
        for t in v:
            cur=cur+1 if t else 0; best=max(best,cur)
        return best>=L
    if cs_guess is None: cs_guess=min(bx1-bx0,by1-by0)/2
    vcols=[x for x in range(bx0,bx1+1) if runs_long(sub[by0:by1+1,x], int(cs_guess*0.8))]
    hrows=[y for y in range(by0,by1+1) if runs_long(sub[y,bx0:bx1+1], int(cs_guess*0.8))]
    def cl(v):
        out=[]
        for t in v:
            if out and t-out[-1][-1]<=3: out[-1].append(t)
            else: out.append([t])
        return [int(np.mean(c)) for c in out]
    V=cl(vcols); Hh=cl(hrows)
    cs=np.median(np.diff(V)) if len(V)>1 else cs_guess
    cells={}
    for i in range(len(Hh)-1):
        for j in range(len(V)-1):
            ya,yb,xa,xb=Hh[i],Hh[i+1],V[j],V[j+1]
            if abs((yb-ya)-cs)>cs*0.25 or abs((xb-xa)-cs)>cs*0.25: continue
            # border check: top/bottom/left/right edges mostly dark
            def frac_h(y,xa,xb): return sub[max(0,y-2):y+3, xa+3:xb-3].any(0).mean()
            def frac_v(x,ya,yb): return sub[ya+3:yb-3, max(0,x-2):x+3].any(1).mean()
            if min(frac_h(ya,xa,xb),frac_h(yb,xa,xb),frac_v(xa,ya,yb),frac_v(xb,ya,yb))>THRESH:
                r=round((ya-Hh[0])/cs); c=round((xa-V[0])/cs)
                cells[(r,c)]=((x0+xa,y0+ya),(x0+xb,y0+ya),(x0+xa,y0+yb))
    return cells, cs
