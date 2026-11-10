import sys
sys.path.insert(0, '/home/user/work/out2/PD2C/verify')
from verify_d06 import *
P4='甲乙丙丁'
M=[]
for ms in product(B,repeat=4):
    for cpa in product(B,repeat=4):
        for gj in product(B,repeat=4):
            if sum(ms)!=3 or sum(cpa)!=2 or sum(gj)!=1: continue
            allthree=[i for i in range(4) if ms[i] and cpa[i] and gj[i]]
            if len(allthree)!=1: continue
            if any(not(ms[i] or cpa[i] or gj[i]) for i in range(4)): continue
            if ms[0]!=ms[3]: continue
            if cpa[1]!=cpa[2]: continue
            if ms[2]+ms[3]!=1: continue
            M.append(P4[allthree[0]])
print(M)
judge('GDXD2019SW-45',M,{k:(lambda x:(lambda m:m==x))(x) for k,x in zip('ABCD',P4)},'must','B')
# GD2023X-58
cand={'甲':('高一','史'),'乙':('高一','地'),'丙':('高一','政'),'丁':('高二','地'),'戊':('高二','语'),'己':('高三','政'),'庚':('高三','数')}
def ok(g):
    gr=[cand[x][0] for x in g]; sb=[cand[x][1] for x in g]
    return gr.count('高一')==2 and gr.count('高二')==1 and gr.count('高三')==1 and len(set(sb))==4
opts={'A':'甲乙丁庚','B':'甲乙戊己','C':'乙丙戊己','D':'乙戊己庚'}
record('GD2023X-58',''.join(k for k,v in opts.items() if ok(v)),'B','groups satisfying')
