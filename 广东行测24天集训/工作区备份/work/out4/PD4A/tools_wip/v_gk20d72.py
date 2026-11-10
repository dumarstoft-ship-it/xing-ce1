"""GK2020D-72: read unit-square layouts (B=black, W=white, lower-case with dot) and compare with the simulated rule:
odd steps: black L-tromino rotates 90° clockwise about its dotted corner; even steps: white L-tromino rotates 90° counter-clockwise; black on top"""
from panels import *
a=load('as/GK2020D-72.png'); bx=boxes(a)
U=None
def read(box):
    global U
    sub=crop(a,box,8); m=sub<128; ys,xs=np.where(m)
    x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
    # unit size: estimate from black-dot-free runs: use known approx 0.108 inch -> try candidates
    best=None
    for u in np.arange(24,32,0.25):
        nx=(x1-x0)/u; ny=(y1-y0)/u
        err=abs(nx-round(nx))+abs(ny-round(ny))
        if best is None or err<best[0]: best=(err,u,round(nx),round(ny))
    _,u,nx,ny=best
    ux=(x1-x0)/nx; uy=(y1-y0)/ny
    g=[]
    for j in range(ny):
        row=''
        for i in range(nx):
            cx0=x0+i*ux; cy0=y0+j*uy
            cell=sub[int(cy0+0.15*uy):int(cy0+0.85*uy), int(cx0+0.15*ux):int(cx0+0.85*ux)]
            ring=sub[int(cy0+0.15*uy):int(cy0+0.3*uy), int(cx0+0.15*ux):int(cx0+0.85*ux)]
            centre=sub[int(cy0+0.38*uy):int(cy0+0.62*uy), int(cx0+0.38*ux):int(cx0+0.62*ux)]
            # borders present?
            top=m[int(cy0)-2:int(cy0)+4, int(cx0+0.2*ux):int(cx0+0.8*ux)].any(0).mean() if cy0>=2 else m[0:4,int(cx0+0.2*ux):int(cx0+0.8*ux)].any(0).mean()
            bot=m[int(cy0+uy)-4:int(cy0+uy)+3, int(cx0+0.2*ux):int(cx0+0.8*ux)].any(0).mean()
            frac=(cell<128).mean()
            if frac>0.6:
                # black; white dot somewhere inside?
                lab,n=nd.label(cell>=128); has=any((lab==k).sum()>12 for k in range(1,n+1))
                row+='b' if has else 'B'
            elif top>0.8 and bot>0.8:
                lab,n=nd.label(cell<128); has=any((lab==k).sum()>12 for k in range(1,n+1))
                row+='w' if has else 'W'
            else: row+='.'
        g.append(row)
    return g
names=['f1','f2','f3','f4','f5','?','A','B','C','D']; R={}; k=0
for band in bx:
    for b in band:
        if names[k]!='?': R[names[k]]=read(b)
        k+=1
for n in R: print(n); print('\n'.join(R[n]))
# ---- simulation
def rot_cw(v): x,y=v; return (-y,x)      # image coords (y down): right(1,0)->down(0,1)
def rot_ccw(v): x,y=v; return (y,-x)
def render(wa,ba):
    cells={}
    wc=(0,0); bc=(1,-1)
    for d in [(0,0)]+list(wa): cells[(wc[0]+d[0],wc[1]+d[1])]='w' if d==(0,0) else 'W'
    for d in [(0,0)]+list(ba): cells[(bc[0]+d[0],bc[1]+d[1])]='b' if d==(0,0) else 'B'   # black on top
    xs=[c[0] for c in cells]; ys=[c[1] for c in cells]
    return [''.join(cells.get((x,y),'.') for x in range(min(xs),max(xs)+1)) for y in range(min(ys),max(ys)+1)]
wa=[(-1,0),(0,1)]; ba=[(1,0),(0,1)]   # fig1: white arms left & down; black arms right & down
sim=[render(wa,ba)]
for step in range(1,6):
    if step%2==1: ba=[rot_cw(v) for v in ba]
    else: wa=[rot_ccw(v) for v in wa]
    sim.append(render(wa,ba))
def trim(g):
    g=[r for r in g if set(r)!={'.'}]
    while all(r[0]=='.' for r in g): g=[r[1:] for r in g]
    while all(r[-1]=='.' for r in g): g=[r[:-1] for r in g]
    return g
for i in range(5): print('sim fig',i+1,trim(sim[i]),'== read',trim(sim[i])==trim(R[f'f{i+1}']))
print('sim fig 6',trim(sim[5]))
for k in 'ABCD': print(k,trim(R[k]),trim(R[k])==trim(sim[5]))
