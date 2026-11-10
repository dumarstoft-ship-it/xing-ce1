import itertools
M=['甲','乙','丙','丁','戊','己','庚','辛']
QS=[]
for qs in itertools.product(range(1,5),repeat=8):
    q=dict(zip(M,qs))
    if any(sum(1 for v in qs if v==k)>3 for k in range(1,5)): continue
    if q['丁']!=2 or q['辛']!=2 or q['甲']!=q['戊']: continue
    if not(q['乙']<q['丁']<q['丙']): continue
    if not(q['己']<q['丙']<q['甲']): continue
    QS.append(q)
print('strict-quarter assignments',len(QS))
def cnt(q,k): return sum(1 for v in q.values() if v==k)
print('P07',{k:any(q[a]==1 and q[b]==1 for q in QS) for k,(a,b) in {'A':('甲','戊'),'B':('丙','丁'),'C':('丁','己'),'D':('己','庚')}.items()})
S=[q for q in QS if cnt(q,2)==2]; print('P08 n',len(S),{k:all(q[m]==1 for q in S) for k,m in {'A':'甲','B':'乙','C':'庚','D':'丙'}.items()})
S=[q for q in QS if q['丙']==4 and q['戊']==4]; print('P09 n',len(S),{k:any(q[a]==3 and q[b]==3 for q in S) for k,(a,b) in {'A':('甲','庚'),'B':('乙','丁'),'C':('乙','己'),'D':('己','庚')}.items()})
S=[q for q in QS if all(cnt(q,i)>=1 for i in (1,2,3,4)) and cnt(q,4)==1]; print('P10 n',len(S),{k:(len(S)>0 and all(q[a]==3 and q[b]==3 for q in S)) for k,(a,b) in {'A':('甲','戊'),'B':('乙','丙'),'C':('丙','己'),'D':('己','庚')}.items()})
S=[q for q in QS if q['甲']==3 and cnt(q,4)==0]; print('P11 n',len(S),{k:any(q['庚']==q[m] for q in S) for k,m in {'A':'乙','B':'丙','C':'己','D':'辛'}.items()})
