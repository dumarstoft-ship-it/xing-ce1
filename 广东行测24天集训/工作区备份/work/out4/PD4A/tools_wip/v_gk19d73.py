"""GK2019D-73: read the 12 unit edges of the 2x2 lattice for rows 2,3 and the options; check (fig1 XOR fig2) rotated 90° == fig3"""
from panels import *
a=load('as/GK2019D-73.png')
bx=boxes(a, hlen=250, minw=100, minh=100)
show(a,bx)
E=[]  # 12 unit edges as ((x0,y0),(x1,y1)) on lattice 0..2
for y in range(3):
    for x in range(2): E.append(((x,y),(x+1,y)))
for x in range(3):
    for y in range(2): E.append(((x,y),(x,y+1)))
def edges(box):
    sub=crop(a,box,8); m=sub<150; ys,xs=np.where(m)
    x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max(); w=(x1-x0)/2; h=(y1-y0)/2
    S=set()
    for (p,q) in E:
        # sample along the edge, fraction of dark within +-4px
        n=0;t=0
        for k in range(3,18):
            f=k/20; X=x0+(p[0]+(q[0]-p[0])*f)*w; Y=y0+(p[1]+(q[1]-p[1])*f)*h
            t+=1; n+= m[max(0,int(Y)-4):int(Y)+5, max(0,int(X)-4):int(X)+5].any()
        if n/t>0.8: S.add((p,q))
    return frozenset(S)
def rot(S,cw=True):
    def r(p):
        x,y=p
        return (2-y,x) if cw else (y,2-x)   # image coords (y down): clockwise (x,y)->(2-y,x)
    out=set()
    for p,q in S:
        a_,b_=r(p),r(q); out.add((min(a_,b_),max(a_,b_)))
    return frozenset(out)
def norm(S): return frozenset((min(p,q),max(p,q)) for p,q in S)
def draw(S):
    g=[[' ']*5 for _ in range(5)]
    for (p,q) in S:
        (x0,y0),(x1,y1)=p,q
        if y0==y1: g[2*y0][2*min(x0,x1)+1]='─'
        else: g[2*min(y0,y1)+1][2*x0]='│'
    for y in range(0,5,2):
        for x in range(0,5,2): g[y][x]='·'
    return '\n'.join(''.join(r) for r in g)
names=[['11','12','13'],['21','22','23'],['31','32','Q','A','B','C','D']]
F={}
for band,nm in zip(bx,names):
    for b,n in zip(band,nm):
        if n in ('11','12','13','Q'): continue
        F[n]=norm(edges(b))
for n in ('21','22','23','31','32','A','B','C','D'):
    print(n, len(F[n])); print(draw(F[n]))
x2=norm(F['21']^F['22']); print('row2 XOR:'); print(draw(x2)); print('row2: rot CW == fig3',rot(x2,True)==F['23'],' rot CCW == fig3',rot(x2,False)==F['23'],' unrotated == fig3', x2==F['23'])
x3=norm(F['31']^F['32']); print('row3 XOR:'); print(draw(x3))
for k in 'ABCD':
    print(k,'== XOR',F[k]==x3,'| == XOR rot CW',F[k]==rot(x3,True),'| == XOR rot CCW',F[k]==rot(x3,False))
print('rot CCW of row3 XOR:'); print(draw(rot(x3,False)))
