import sys
sys.path.insert(0, '/home/user/work/out2/PD2C/verify')
from verify_d06 import *
for R in (1,-1):
  for derange in (True, False):
    M=[]
    for chairs in permutations([1,2,3,4,5]):
        if chairs[0]!=1: continue          # fix rotation: chair 1 at position 0
        pos={c:i for i,c in enumerate(chairs)}
        for ppl in permutations('甲乙丙丁戊'):
            P={p:chairs[i] for i,p in enumerate(ppl)}      # person -> chair number
            at=lambda c,k: chairs[(pos[c]+k)%5]           # chair number k steps (k>0 right if R=1)
            if P['甲']!=at(1,2*R): continue
            if P['乙']!=at(5,-2*R): continue
            if P['丙']!=at(3,-1*R): continue
            if P['丁']!=at(2,-1*R): continue
            if derange and any(P[p]==i+1 for i,p in enumerate('甲乙丙丁戊')): continue
            if P['丙']!=1: continue
            M.append(P)
    print('R',R,'derange',derange,'models',len(M),[m['甲'] for m in M])
