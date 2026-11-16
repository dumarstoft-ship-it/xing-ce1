# Q50: fold each net and test against the two cubes of the cuboid.
# Net cells: (col,row) -> pattern. Patterns:
#   ('B',cx,cy)  black quarter square at net corner (cx,cy) (0=left/top, 1=right/bottom)
#   ('O',cx,cy)  outlined quarter square (two lines from edge midpoints to centre) at corner
#   ('T',dir)    isosceles triangle whose base lies on edge dir in {'L','R','U','D'}
#   None         blank
import itertools
NETS={
 1:{(2,0):('B',1,1),(0,1):('T','D'),(1,1):None,(2,1):None,(3,1):('O',0,0),(3,2):None},
 2:{(1,0):('T','U'),(0,1):('B',1,1),(1,1):None,(2,1):None,(2,2):None,(3,2):('O',0,1)},
 3:{(1,0):('O',0,0),(1,1):('B',0,1),(2,1):None,(3,1):('T','U'),(0,2):None,(1,2):None},
 4:{(0,0):None,(1,0):None,(1,1):('T','L'),(2,1):('B',1,1),(2,2):('O',1,0),(3,2):None},
}
def neg(v): return tuple(-a for a in v)
def add(*vs): return tuple(sum(x) for x in zip(*vs))
def mul(k,v): return tuple(k*a for a in v)

def fold(net):
    start=next(iter(net))
    frames={start:((0,-1,0),(1,0,0),(0,0,-1))}   # n,r,d : start face = front
    q=[start]
    while q:
        c=q.pop(0); n,r,d=frames[c]
        for (dc,dr),f in {(1,0):lambda n,r,d:(r,neg(n),d),(-1,0):lambda n,r,d:(neg(r),n,d),
                          (0,1):lambda n,r,d:(d,r,neg(n)),(0,-1):lambda n,r,d:(neg(d),r,n)}.items():
            nb=(c[0]+dc,c[1]+dr)
            if nb in net and nb not in frames:
                frames[nb]=f(n,r,d); q.append(nb)
    faces={}
    for c,p in net.items():
        n,r,d=frames[c]
        assert n not in faces, 'overlap'
        if p is None: faces[n]=None
        elif p[0] in 'BO':
            v=add(n,mul(2*p[1]-1,r),mul(2*p[2]-1,d))
            faces[n]=(p[0],v)
        else:
            e={'L':neg(r),'R':r,'U':neg(d),'D':d}[p[1]]
            faces[n]=('T',e)
    assert len(faces)==6
    return faces

def rotations():
    out=[]
    for perm in itertools.permutations(range(3)):
        for s in itertools.product([1,-1],repeat=3):
            M=[[0]*3 for _ in range(3)]
            for i in range(3): M[i][perm[i]]=s[i]
            det=(M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1])-M[0][1]*(M[1][0]*M[2][2]-M[1][2]*M[2][0])+M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0]))
            if det==1: out.append(M)
    return out
ROT=rotations()
def ap(M,v): return tuple(sum(M[i][j]*v[j] for j in range(3)) for i in range(3))
def rot_faces(M,faces):
    return {ap(M,n):(None if p is None else (p[0],ap(M,p[1]))) for n,p in faces.items()}

# cuboid frame: X right, Y away from viewer, Z up. front normal (0,-1,0), top (0,0,1), right (1,0,0)
FRONT,TOP,RIGHT=(0,-1,0),(0,0,1),(1,0,0)
REQ={
 'L(left cube)': {FRONT:('B',(-1,-1,-1)), TOP:('O',(-1,-1,1))},
 'R(right cube)':{FRONT:('T',(0,0,-1)), TOP:('B',(1,1,1)), RIGHT:('O',(1,1,1))},
}
for k,net in NETS.items():
    faces=fold(net)
    res=[]
    for name,req in REQ.items():
        ok=any(all(rot_faces(M,faces)[n]==p for n,p in req.items()) for M in ROT)
        res.append('%s:%s'%(name,'YES' if ok else 'no'))
    print('net',k,' '.join(res))
