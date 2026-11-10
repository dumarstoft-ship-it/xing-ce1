import sys, collections
sys.path.insert(0, '/home/user/work/out2/PD2C/verify')
from verify_d06 import *
P8='甲乙丙丁戊己庚辛'
M=[]
for p in permutations(range(1,9)):
    P=dict(zip(P8,p))
    if abs(P['甲']-P['丙'])!=4 or abs(P['乙']-P['己'])!=3 or P['庚']-P['丁']!=3 or abs(P['辛']-P['戊'])!=2: continue
    M.append(P)
def show(MM):
    for m in MM: print('   ', ''.join(sorted(m,key=m.get)))
# candidate added conditions
conds={}
for x in P8:
    for k in range(1,9): conds[f'{x}在第{k}间']=lambda P,x=x,k=k:P[x]==k
for x,y in combinations(P8,2):
    conds[f'{x}与{y}相邻']=lambda P,x=x,y=y:abs(P[x]-P[y])==1
    conds[f'{x}在{y}左边']=lambda P,x=x,y=y:P[x]<P[y]
    conds[f'{y}在{x}左边']=lambda P,x=x,y=y:P[y]<P[x]
res=[]
for name,f in conds.items():
    MM=[m for m in M if f(m)]
    if not MM: continue
    forced=[(x,MM[0][x]) for x in P8 if all(m[x]==MM[0][x] for m in MM)]
    res.append((len(MM),name,forced))
res.sort()
for r in res:
    print(r)
