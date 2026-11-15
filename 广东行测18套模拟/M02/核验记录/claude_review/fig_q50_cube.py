import numpy as np, itertools
# Net coordinates: (row, col), row increases downward. In-face 2D vectors use math coords: +x right, +y up.
# Pattern codes:
#  'D' big diamond (D4-symmetric), 'X' cross/田 (D4), 'O' blank (D4)
#  'M' midline: unsigned line direction
#  'L' off-centre parallel line: signed vector pointing to the edge it hugs
#  'N' narrow diamond: signed vector pointing to the edge it touches (long axis parallel to that edge)
L,R,U,Dn=(-1,0),(1,0),(0,1),(0,-1)
nets={
 'A':{(0,0):('M',U),(1,0):('D',None),(1,1):('O',None),(1,2):('L',L),(1,3):('X',None),(2,1):('N',L)},
 'B':{(0,1):('X',None),(1,0):('D',None),(1,1):('N',L),(1,2):('L',Dn),(1,3):('M',R),(2,2):('O',None)},
 'C':{(0,0):('X',None),(0,1):('M',U),(1,1):('D',None),(1,2):('O',None),(1,3):('L',L),(2,2):('N',L)},
 'D':{(0,1):('O',None),(1,0):('D',None),(1,1):('N',L),(1,2):('L',U),(2,2):('X',None),(2,3):('M',U)},
}
def fold(net):
    start=sorted(net)[0]
    frames={start:(np.array([0,0,1]),np.array([1,0,0]),np.array([0,1,0]))}  # n,u,v
    todo=[start]
    while todo:
        cell=todo.pop()
        n,u,v=frames[cell]
        r,c=cell
        for (dr,dc) in ((0,1),(0,-1),(-1,0),(1,0)):
            nb=(r+dr,c+dc)
            if nb in net and nb not in frames:
                if (dr,dc)==(0,1):  nf=(u,-n,v)     # right
                if (dr,dc)==(0,-1): nf=(-u,n,v)     # left
                if (dr,dc)==(-1,0): nf=(v,u,-n)     # up (row-1)
                if (dr,dc)==(1,0):  nf=(-v,u,n)     # down (row+1)
                frames[nb]=nf; todo.append(nb)
    cube={}
    for cell,(pat,vec) in net.items():
        n,u,v=frames[cell]
        f=None if vec is None else tuple(int(x) for x in vec[0]*u+vec[1]*v)
        key=tuple(int(x) for x in n)
        assert key not in cube, 'overlap -> not a valid net'
        cube[key]=(pat,f,cell)
    assert len(cube)==6
    return cube
def rotations():
    mats=[]
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1,-1),repeat=3):
            M=np.zeros((3,3),int)
            for i,(p,s) in enumerate(zip(perm,signs)): M[i,p]=s
            if round(np.linalg.det(M))==1: mats.append(M)
    return mats
ROTS=rotations(); assert len(ROTS)==24
def same(c1,c2):
    hits=[]
    for M in ROTS:
        ok=True
        for n,(p,f,_) in c1.items():
            n2=tuple(int(x) for x in M@np.array(n))
            p2,f2,_=c2[n2]
            if p!=p2: ok=False;break
            if f is not None:
                g=tuple(int(x) for x in M@np.array(f))
                if p=='M':
                    if g!=f2 and tuple(-x for x in g)!=f2: ok=False;break
                else:
                    if g!=f2: ok=False;break
        if ok: hits.append(M)
    return hits
cubes={k:fold(v) for k,v in nets.items()}
names={'D':'big-diamond','X':'cross','O':'blank','M':'midline','L':'offset-line','N':'narrow-diamond'}
for k,c in cubes.items():
    opp={}
    for n,(p,f,cell) in c.items():
        m=tuple(-x for x in n)
        if p<c[m][0]: opp[p]=c[m][0]
    print(k,'opposite pairs:',sorted((names[a],names[b]) for a,b in opp.items()))
print()
for a,b in itertools.combinations('ABCD',2):
    print(a,b,'same cube' if same(cubes[a],cubes[b]) else 'DIFFERENT')
print()
# Describe, for each net, the local relations that decide it
def nb_dir(c,pat):
    for n,(p,f,_) in c.items():
        if p==pat: return n,f
for k,c in cubes.items():
    nN,fN=nb_dir(c,'N'); nL,fL=nb_dir(c,'L'); nM,fM=nb_dir(c,'M')
    print(k,'narrow-diamond hugs the edge shared with:',names[c[fN][0]],
          '| offset-line hugs edge shared with:',names[c[fL][0]],
          '| midline runs toward:',names[c[fM][0]],'/',names[c[tuple(-x for x in fM)][0]])

print()
# Chirality: sign of det[n(big-diamond), n(blank), n(narrow-diamond)] seen from outside
for k,c in cubes.items():
    pos={p:np.array(n) for n,(p,f,_) in c.items()}
    t=int(np.linalg.det(np.array([pos['D'],pos['O'],pos['N']])))
    t2=int(np.linalg.det(np.array([pos['D'],pos['X'],pos['M']])))
    order='counter-clockwise' if t>0 else 'clockwise'
    print(k,'det(Dmd,Blank,Narrow)=%+d'%t,' det(Dmd,Cross,Mid)=%+d'%t2, ' -> big-diamond->blank->narrow-diamond is',order,'seen from outside the shared corner')
# Also: does mirroring B's net give the A/C/D cube?
def mirror_net(net):
    out={}
    for (r,c),(p,f) in net.items():
        g=None if f is None else (-f[0],f[1])
        out[(r,-c)]=(p,g)
    return out
mB=fold(mirror_net(nets['B']))
print('mirror(B) same as A?', bool(same(mB,cubes['A'])))
# Robustness: if the narrow-diamond orientation or offset-line side were misread, is the odd-one-out still unique?
import copy
