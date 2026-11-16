"""Q50 展开图折叠核验.
长方体 = 左正方体L(x∈[0,1]) + 右正方体R(x∈[1,2]); 坐标 x右 y上 z朝前(z=1为正面).
题图读出的可见面:
  L 正面: 黑色小方块在左下角(顶点(0,0,1));  L 顶面: 空心小方块在前左角(顶点(0,1,1)).
  R 正面: 三角形底边在下边(棱 (0,0,1)-(1,0,1), R自身坐标);
  R 顶面: 黑色小方块在后右角(顶点(1,1,0));  R 右面: 空心小方块在上后角(顶点(1,1,0)).
四个展开图(行,列)->图案: K=黑方块, O=空心方块(角: tl/tr/bl/br), T=三角形(底边: t/b/l/r).
"""
import itertools
NETS={
 '①':{(0,2):('K','br'),(1,0):('T','b'),(1,1):None,(1,2):None,(1,3):('O','tl'),(2,3):None},
 '②':{(0,1):('T','t'),(1,0):('K','br'),(1,1):None,(1,2):None,(2,2):None,(2,3):('O','bl')},
 '③':{(0,1):('O','tl'),(1,1):('K','bl'),(1,2):None,(1,3):('T','t'),(2,0):None,(2,1):None},
 '④':{(0,0):None,(0,1):None,(1,1):('T','l'),(1,2):('K','br'),(2,2):('O','tr'),(2,3):None},
}
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def neg(a): return tuple(-x for x in a)
def cross(a,b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def fold(net):
    root=sorted(net)[0]
    frames={root:((0,1,1),(1,0,0),(0,-1,0))}  # O(top-left corner), R(right), D(down)
    stack=[root]
    while stack:
        c=stack.pop(); O,R,D=frames[c]; N=cross(D,R)
        for dc,(O2,R2,D2) in {(0,1):(add(O,R),neg(N),D),(0,-1):(sub(O,N),N,D),
                              (1,0):(add(O,D),R,neg(N)),(-1,0):(sub(O,N),R,N)}.items():
            n=(c[0]+dc[0],c[1]+dc[1])
            if n in net and n not in frames:
                frames[n]=(O2,R2,D2); stack.append(n)
    assert len(frames)==6
    normals={cross(D,R) for (O,R,D) in frames.values()}
    assert len(normals)==6, 'not a valid cube net'
    faces={}
    for c,(O,R,D) in frames.items():
        N=cross(D,R); f=net[c]
        if f is None: feat=None
        elif f[0] in 'KO':
            pt={'tl':O,'tr':add(O,R),'bl':add(O,D),'br':add(add(O,R),D)}[f[1]]
            feat=(f[0],pt)
        else:
            e={'t':(O,add(O,R)),'b':(add(O,D),add(add(O,R),D)),'l':(O,add(O,D)),'r':(add(O,R),add(add(O,R),D))}[f[1]]
            feat=('T',frozenset(e))
        faces[N]=feat
    return faces
def rotations():
    mats=[]
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product([1,-1],repeat=3):
            M=[[0]*3 for _ in range(3)]
            for i in range(3): M[i][perm[i]]=signs[i]
            d=(M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1])-M[0][1]*(M[1][0]*M[2][2]-M[1][2]*M[2][0])+M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0]))
            if d==1: mats.append(M)
    return mats
def rotv(M,v): return tuple(sum(M[i][j]*v[j] for j in range(3)) for i in range(3))
def rotp(M,p):  # rotate point about cube centre (0.5,0.5,0.5); use doubled coords to stay integer
    q=tuple(2*x-1 for x in p); r=rotv(M,q); return tuple((x+1)//2 for x in r)
def rotated(faces,M):
    out={}
    for N,f in faces.items():
        if f is None: g=None
        elif f[0] in 'KO': g=(f[0],rotp(M,f[1]))
        else: g=('T',frozenset(rotp(M,p) for p in f[1]))
        out[rotv(M,N)]=g
    return out
FRONT,TOP,RIGHT=(0,0,1),(0,1,0),(1,0,0)
def fits_L(F): return F[FRONT]==('K',(0,0,1)) and F[TOP]==('O',(0,1,1))
def fits_R(F): return (F[FRONT]==('T',frozenset({(0,0,1),(1,0,1)})) and F[TOP]==('K',(1,1,0))
                       and F[RIGHT]==('O',(1,1,0)))
ROTS=rotations(); assert len(ROTS)==24
res={}
for k,net in NETS.items():
    faces=fold(net)
    L=any(fits_L(rotated(faces,M)) for M in ROTS)
    R=any(fits_R(rotated(faces,M)) for M in ROTS)
    res[k]=(L,R)
    print(k,'可作左正方体:',L,' 可作右正方体:',R)
for opt,(a,b) in {'A':('②','④'),'B':('②','③'),'C':('①','④'),'D':('①','③')}.items():
    ok=(res[a][0] and res[b][1]) or (res[a][1] and res[b][0])
    print(opt,a,b,'->', '可以' if ok else '不行')
names={(0,0,1):'正面',(0,1,0):'顶面',(1,0,0):'右面',(-1,0,0):'左面',(0,-1,0):'底面',(0,0,-1):'后面'}
for k,role,fn in [('②','左正方体',fits_L),('④','右正方体',fits_R)]:
    for M in ROTS:
        F=rotated(fold(NETS[k]),M)
        if fn(F):
            print(k,'作',role,'时各面:',{names[n]:(f[0] if f else '空白') for n,f in F.items()})
