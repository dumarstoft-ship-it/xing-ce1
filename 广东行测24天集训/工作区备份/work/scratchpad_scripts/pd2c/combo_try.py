import sys
sys.path.insert(0, '/home/user/work/out2/PD2C/verify')
from verify_d06 import *

# GK2021D 106-110
DEP = ['人事', '科研', '教育', '财务', '宣传', '后勤', '工会']
def gk2021d_models():
    M = []
    for a in product('王卫丁', repeat=7):
        P = dict(zip(DEP, a))
        if P['教育'] != P['财务'] or P['宣传'] != P['后勤']: continue
        cnt = {x: a.count(x) for x in '王卫丁'}
        if not cnt['丁'] > cnt['卫']: continue
        if (P['教育'] == '王') + (P['工会'] == '王') != 1: continue
        if (P['工会'] == '卫') + (P['后勤'] == '卫') != 1: continue
        M.append(P)
    return M
M = gk2021d_models(); print('GK2021D base models', len(M))
for m in M: print('  ', {x: [d for d in DEP if m[d] == x] for x in '王卫丁'})
