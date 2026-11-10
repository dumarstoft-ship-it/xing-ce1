"""Parse a grid net (unit squares with dark borders, gray/white fill) from a grayscale image region.
parse(a, x0,y0,x1,y1) -> dict (row,col)->'G'/'W'/'B' (gray/white/black), plus pitch"""
import numpy as np
def runs(v):
    out=[];s=None
    for i,x in enumerate(v):
        if x and s is None: s=i
        if not x and s is not None: out.append((s,i-1)); s=None
    if s is not None: out.append((s,len(v)-1))
    return out
def lines(mask, axis, minlen):
    # positions where a long dark run exists along the axis
    L=mask.shape[1-axis]
    pos=[]
    for i in range(mask.shape[axis]):
        line=mask[i,:] if axis==0 else mask[:,i]
        best=max([b-a+1 for a,b in runs(line)] or [0])
        if best>=minlen: pos.append(i)
    # cluster
    cl=[]
    for p in pos:
        if cl and p-cl[-1][-1]<=2: cl[-1].append(p)
        else: cl.append([p])
    return [float(np.mean(c)) for c in cl]
def parse(a, x0,y0,x1,y1, dark=80, minlen=8, gray_hi=200, black_lo=60):
    sub=a[y0:y1,x0:x1]; m=sub<dark
    H=lines(m,0,minlen); V=lines(m,1,minlen)
    pitch=np.median(np.diff(V)) if len(V)>1 else None
    cells={}
    for i in range(len(H)-1):
        for j in range(len(V)-1):
            ya,yb,xa,xb=H[i],H[i+1],V[j],V[j+1]
            if abs((yb-ya)-pitch)>pitch*0.35 or abs((xb-xa)-pitch)>pitch*0.35: continue
            ia,ib,ja,jb=int(round(ya)),int(round(yb)),int(round(xa)),int(round(xb))
            def edge_h(y): return m[max(0,y-1):y+2, ja+2:jb-1].any(0).mean()
            def edge_v(x): return m[ia+2:ib-1, max(0,x-1):x+2].any(1).mean()
            if min(edge_h(ia),edge_h(ib),edge_v(ja),edge_v(jb))<0.85: continue
            inner=sub[ia+3:ib-2, ja+3:jb-2]
            mv=np.median(inner)
            col='B' if mv<black_lo else ('G' if mv<gray_hi else 'W')
            r=int(round((ya-H[0])/pitch)); c=int(round((xa-V[0])/pitch))
            cells[(r,c)]=col
    return cells, pitch
def show(cells):
    R=max(r for r,c in cells)+1; C=max(c for r,c in cells)+1
    return '\n'.join(''.join(cells.get((r,c),' ') for c in range(C)) for r in range(R))

def fit_grid(pos, pitch_guess):
    """fit regular grid origin+pitch to line positions"""
    pos=np.array(sorted(pos)); best=None
    for p in np.arange(pitch_guess*0.8, pitch_guess*1.2, 0.05):
        for o in np.arange(0,p,0.25):
            k=np.round((pos-o)/p); err=np.abs(pos-(o+k*p))
            s=(np.minimum(err,2.0)).sum()
            if best is None or s<best[0]: best=(s,o,p)
    return best[1],best[2]
def thin_lines(m, axis, maxw=4):
    out=[]
    M=m if axis==1 else m.T   # scan rows (axis=1 -> vertical lines found along rows)
    for row in M:
        for a,b in runs(row):
            if b-a+1<=maxw: out.append((a+b)/2)
    return out
def parse2(a, x0,y0,x1,y1, pitch_guess, dark=100, white=200):
    sub=a[y0:y1,x0:x1]; m=sub<dark
    vx=thin_lines(m,1); hy=thin_lines(m,0)
    ox,px=fit_grid(vx,pitch_guess); oy,py=fit_grid(hy,pitch_guess)
    cells={}
    nx=int((sub.shape[1]-ox)/px)+1; ny=int((sub.shape[0]-oy)/py)+1
    for i in range(-1,ny):
        for j in range(-1,nx):
            ya,yb=oy+i*py, oy+(i+1)*py; xa,xb=ox+j*px, ox+(j+1)*px
            if ya<0 or xa<0 or yb>=sub.shape[0] or xb>=sub.shape[1]: continue
            ia,ib,ja,jb=int(round(ya)),int(round(yb)),int(round(xa)),int(round(xb))
            inner=sub[ia+3:ib-2, ja+3:jb-2]
            if inner.size==0: continue
            mv=np.median(inner)
            def edge_h(y): return m[max(0,y-1):y+2, ja+3:jb-2].any(0).mean()
            def edge_v(x): return m[ia+3:ib-2, max(0,x-1):x+2].any(1).mean()
            borders=min(edge_h(ia),edge_h(ib),edge_v(ja),edge_v(jb))
            if mv<dark: cells[(i,j)]='G'
            elif mv>white and borders>0.85: cells[(i,j)]='W'
            elif mv<=white and mv>=dark and borders>0.85: cells[(i,j)]='G'
    # normalise indices
    r0=min(r for r,c in cells); c0=min(c for r,c in cells)
    return {(r-r0,c-c0):v for (r,c),v in cells.items()}, (ox,px,oy,py)
