import sys
sys.path.insert(0, '/home/user/work/out2/PD2C/verify')
from verify_d06 import *

# GK2017F-115
M=[]
for p in permutations(['行政','销售','研发','安保']):
    P=dict(zip('张王李赵',p))
    if P['张'] in ('行政','安保') or P['王'] in ('行政','研发') or P['李'] in ('行政','安保') or P['赵'] in ('研发','安保'): continue
    if not imp(P['张']!='研发', P['赵']!='行政'): continue
    M.append(P)
print('GK2017F-115', M)
judge('GK2017F-115', M, {'A':lambda P:P['张']=='销售' and P['李']=='研发','B':lambda P:P['赵']=='研发' and P['李']=='销售','C':lambda P:P['李']=='销售' and P['张']=='研发','D':lambda P:P['李']=='研发' and P['赵']=='安保'},'must','C')

# GD2022X-62 : 2 seventh-grade + 1 eighth-grade, subjects distinct
sev={'甲':'语','乙':'数','丙':'英'}; eig={'丁':'数','戊':'史','己':'语'}
def ok(g):
    s=[x for x in g if x in sev]; e=[x for x in g if x in eig]
    subj=[sev.get(x) or eig.get(x) for x in g]
    return len(s)==2 and len(e)==1 and len(set(subj))==3
opts={'A':'甲己戊','B':'甲乙己','C':'乙丙戊','D':'乙丙丁'}
record('GD2022X-62', ''.join(k for k,v in opts.items() if ok(v)), 'C', 'groups satisfying')

# GD2023X-56
M=[]
for a in product('ABCD', repeat=6):
    P=dict(zip(['甲','乙','丙','张','李','王'],a))
    men={P['甲'],P['乙'],P['丙']}; women={P['张'],P['李'],P['王']}
    if not men<=women: continue
    if P['张'] not in 'AB' or P['乙']!='D': continue
    if P['李']!='C': continue
    M.append(P)
judge('GD2023X-56', M, {'A':lambda P:P['丙']=='A','B':lambda P:P['张']=='B','C':lambda P:P['甲']=='C','D':lambda P:P['王']=='D'},'must','D')

# JS2023A-93
M=[]
for age in product('青中',repeat=5):
    if age.count('青')!=3: continue
    for sub in product('语数',repeat=5):
        if sub.count('语')!=2: continue
        A=dict(zip('甲乙丙丁戊',age)); S=dict(zip('甲乙丙丁戊',sub))
        if A['甲']!=A['丙']: continue
        if A['丁']==A['戊']: continue      # 年龄相差最大 -> 一青一中
        if S['乙']!=S['戊'] or S['丙']==S['丁']: continue
        leaders=[x for x in '甲乙丙丁戊' if A[x]=='中' and S[x]=='语']
        if len(leaders)<1: continue
        for L in leaders: M.append(dict(L=L,A=A,S=S))
print('JS2023A-93 leaders', sorted(set(m['L'] for m in M)), len(M))
judge('JS2023A-93', M, {k:(lambda x:(lambda m:m['L']==x))(x) for k,x in zip('ABCD','甲乙丙丁')},'must','D')

# SZ2023-38 shoes: days 1..7 (Mon..Sun), each day one pair
SH=['篮','滑','牛','凉','拖']
M=[]
for w in product(SH, repeat=7):
    lq=[i for i,x in enumerate(w) if x=='篮']
    if len(lq)!=2 or lq[1]-lq[0]!=4: continue      # 相隔3天 -> 中间隔3天 (差4)
    if w.count('牛')!=1 or w.count('滑')!=1: continue
    n=w.index('牛'); 
    if abs(n-lq[0])!=1: continue
    if not w.index('滑')<lq[1]: continue
    lj=[i for i,x in enumerate(w) if x=='凉']
    if not lj or any(abs(i-lq[0])!=5 for i in lj): continue   # 相隔4天 -> 差5
    if not any(w[i]=='拖' for i in range(lq[0])): continue
    M.append(w)
print('SZ2023-38 (gap=interval days between) models', len(M), M[:5])
