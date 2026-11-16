"""Q60: 一周7天, 游泳(S)3次、跑步(R,健身房)2次, 其余休息(-).
(1)同一天不既游泳又跑步(每天至多一项); (2)不连续两天做同一种运动; (3)周末只运动一天;
(4)周一游泳馆闭馆(周一不游泳); 本周五有聚会不能跑步. 枚举全部可行安排并检验选项."""
from itertools import product
days=['一','二','三','四','五','六','日']
sols=[]
for a in product('SR-',repeat=7):
    if a.count('S')!=3 or a.count('R')!=2: continue
    if (a[5]!='-')+(a[6]!='-')!=1: continue
    if a[0]=='S' or a[4]=='R': continue
    if any(a[i]==a[i+1]!='-' for i in range(6)): continue
    sols.append(a)
for s in sols: print(' '.join(d+':'+x for d,x in zip(days,s)))
print('共',len(sols),'种')
A=any(s[6]=='R' for s in sols)
B=all(s[0]=='R' for s in sols)
C=all({i for i,x in enumerate(s) if x=='S'}<= {3,4,6} for s in sols)
D_cases=[s for s in sols if s[1]=='R']
D=all(s[3]=='R' for s in D_cases) and len(D_cases)>0
print('A 可能周日跑步:',A,'| B 一定周一跑步:',B,'| C 只能在四五日游泳:',C,'| D 若周二跑则周四跑:',D,'(周二跑的方案数',len(D_cases),')')
