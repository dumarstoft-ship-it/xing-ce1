import itertools
M=['甲','乙','丙','丁','戊','己','庚','辛']
scheds=[]
# sizes of quarters, each 0..3, sum 8
for sizes in itertools.product(range(4),repeat=4):
    if sum(sizes)!=8: continue
    for perm in itertools.permutations(M):
        pos={m:i for i,m in enumerate(perm)}
        q={}
        i=0
        for qi,s in enumerate(sizes):
            for _ in range(s):
                q[perm[i]]=qi+1; i+=1
        if q['丁']!=2 or q['辛']!=2: continue
        if q['甲']!=q['戊']: continue
        if not(pos['乙']<pos['丁']<pos['丙']): continue
        if not(pos['己']<pos['丙']<pos['甲']): continue
        scheds.append((sizes,perm,q))
print('total schedules',len(scheds))
qs=set(tuple(sorted(s[2].items())) for s in scheds)
QS=[dict(x) for x in qs]
print('distinct quarter assignments',len(QS))
def cnt(q,k): return sum(1 for v in q.values() if v==k)
# P07
print('P07: which pair can both be in Q1')
for k,pair in {'A':('甲','戊'),'B':('丙','丁'),'C':('丁','己'),'D':('己','庚')}.items():
    print(' ',k,pair,any(q[pair[0]]==1 and q[pair[1]]==1 for q in QS))
# P08
S=[q for q in QS if cnt(q,2)==2]
print('P08: Q2 has 2 -> must be Q1; n=',len(S))
for k,m in {'A':'甲','B':'乙','C':'庚','D':'丙'}.items():
    print(' ',k,m,all(q[m]==1 for q in S), any(q[m]==1 for q in S))
# P09
S=[q for q in QS if q['丙']==4 and q['戊']==4]
print('P09: 丙戊 Q4 -> pair can be Q3; n=',len(S))
for k,pair in {'A':('甲','庚'),'B':('乙','丁'),'C':('乙','己'),'D':('己','庚')}.items():
    print(' ',k,pair,any(q[pair[0]]==3 and q[pair[1]]==3 for q in S))
# P10
S=[q for q in QS if all(cnt(q,i)>=1 for i in (1,2,3,4)) and cnt(q,4)==1]
print('P10: each>=1, Q4==1 -> pair must be Q3; n=',len(S))
for k,pair in {'A':('甲','戊'),'B':('乙','丙'),'C':('丙','己'),'D':('己','庚')}.items():
    print(' ',k,pair,all(q[pair[0]]==3 and q[pair[1]]==3 for q in S))
# P11
S=[q for q in QS if q['甲']==3 and cnt(q,4)==0]
print('P11: 甲Q3, Q4 empty -> 庚 cannot share quarter with; n=',len(S))
for k,m in {'A':'乙','B':'丙','C':'己','D':'辛'}.items():
    print(' ',k,m,'possible together:',any(q['庚']==q[m] for q in S))
