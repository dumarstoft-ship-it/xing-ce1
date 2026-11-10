import sys, collections
sys.path.insert(0, '/home/user/work/out2/PD2C/verify')
from verify_d06 import *
P8='甲乙丙丁戊己庚辛'
M=[]
for p in permutations(range(1,9)):
    P=dict(zip(P8,p))
    if abs(P['甲']-P['丙'])!=4 or abs(P['乙']-P['己'])!=3 or P['庚']-P['丁']!=3 or abs(P['辛']-P['戊'])!=2: continue
    M.append(P)
row=lambda m:''.join(sorted(m,key=m.get))
for name,f in [('丁与戊相邻',lambda P:abs(P['丁']-P['戊'])==1),('乙与戊相邻',lambda P:abs(P['乙']-P['戊'])==1),('庚与辛相邻',lambda P:abs(P['庚']-P['辛'])==1),
               ('甲在丁左边',lambda P:P['甲']<P['丁']),('戊与庚相邻',lambda P:abs(P['戊']-P['庚'])==1),('己与辛相邻',lambda P:abs(P['己']-P['辛'])==1)]:
    MM=[m for m in M if f(m)]
    print(name,len(MM),[row(m) for m in MM])
print('all', sorted(row(m) for m in M))
