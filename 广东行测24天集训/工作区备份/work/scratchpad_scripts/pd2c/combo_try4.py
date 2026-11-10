import sys
sys.path.insert(0, '/home/user/work/out2/PD2C/verify')
from verify_d06 import *
# HB2024-105
P7=['赵','钱','孙','李','周','吴','郑']
M=[]
for am in combinations(P7,4):
    A=set(am); pm=set(P7)-A
    same=lambda x,y:(x in A)==(y in A)
    if same('赵','孙') or same('周','孙'): continue
    if not imp('郑' in pm, '赵' in pm and '李' in pm): continue
    if not (('钱' in A) or ('郑' in pm)): continue
    M.append(A)
print('HB2024-105 models',[sorted(a) for a in M])
judge('HB2024-105',M,{'A':lambda A:{'钱','郑'}<=A,'B':lambda A:{'赵','郑'}<=A,'C':lambda A:{'赵','周'}<=A,'D':lambda A:{'吴','孙'}<=A},'must','A')

# ZJ2024A-102
ppl=['张','王','李','赵','钱','孙']
M=[]
for a in product('甲乙丙丁',repeat=6):
    P=dict(zip(ppl,a)); c={x:a.count(x) for x in '甲乙丙丁'}
    if any(not 1<=c[x]<=2 for x in c): continue
    if not c['乙']>c['甲'] or not c['丁']>c['丙']: continue
    if not imp(P['李']=='甲' or P['赵']=='甲', P['王']=='丁'): continue
    if not imp(any(P[x]=='乙' for x in ['张','李','赵']), [x for x in ppl if P[x]=='丁']==['钱']): continue
    if P['孙']!='丙': continue
    M.append(P)
print('ZJ2024A-102 models',M)
judge('ZJ2024A-102',M,{'A':lambda P:P['张']=='丙','B':lambda P:P['赵']=='乙' and P['钱']=='乙','C':lambda P:P['王']=='丁' and P['李']=='丁','D':lambda P:P['李']=='丁' and P['赵']=='丁'},'must','D')

# GK2020F-111 seats A B C D F, 丁 at B
seats=['A','B','C','D','F']
M=[]
for p in permutations(seats):
    P=dict(zip('甲乙丙丁戊',p))
    if not imp(P['甲']=='C' or P['乙']=='C', P['丙']=='B'): continue
    if not imp(P['戊']=='C', P['丁']=='F'): continue
    if P['丁']!='B': continue
    M.append(P)
judge('GK2020F-111',M,{'A':lambda P:P['甲']=='A','B':lambda P:P['乙']=='D','C':lambda P:P['丙']=='C','D':lambda P:P['戊']=='F'},'must','C')

# SC2025-84
st=['甲','乙','丙','丁','戊','己','庚']
M=[]
for a in product('就研留',repeat=7):
    P=dict(zip(st,a)); c={x:a.count(x) for x in '就研留'}
    if any(not 2<=c[x]<=3 for x in c): continue
    if not imp(P['甲'] in '就留' or P['丙'] in '就留', P['乙']=='研' and P['戊']=='研'): continue
    if not imp(P['乙'] in '就研' or P['丁'] in '就研', P['己']=='留' and P['庚']=='留'): continue
    if not imp(P['戊'] in '研留' or P['己'] in '研留', P['乙']=='就' and P['丙']=='就'): continue
    M.append(P)
print('SC2025-84 models',M)
judge('SC2025-84',M,{'A':lambda P:{x for x in st if P[x]=='留'}=={'甲','乙'},'B':lambda P:{x for x in st if P[x]=='留'}=={'丙','戊'},'C':lambda P:{x for x in st if P[x]=='留'}=={'乙','丁'},'D':lambda P:{x for x in st if P[x]=='留'}=={'丁','庚'}},'must','?')
