import sys, collections
sys.path.insert(0, '/home/user/work/out2/PD2C/verify')
from verify_d06 import *
P8='甲乙丙丁戊己庚辛'
def base():
    M=[]
    for p in permutations(range(1,9)):
        P=dict(zip(P8,p))
        if abs(P['甲']-P['丙'])!=4: continue
        if abs(P['乙']-P['己'])!=3: continue
        if P['庚']-P['丁']!=3: continue
        if abs(P['辛']-P['戊'])!=2: continue
        M.append(P)
    return M
M=base(); print('GK2021F-114 base models',len(M))
print('丁 positions', collections.Counter(m['丁'] for m in M))
judge('GK2021F-114',M,{k:(lambda x:(lambda P:P['丁']==x))(x) for k,x in zip('ABCD',[1,2,3,4])},'cannot','C')
for x in P8: print(x, sorted(collections.Counter(m[x] for m in M).items()))
