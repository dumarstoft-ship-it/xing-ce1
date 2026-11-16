# Q56 and Q60 enumeration
import itertools
# ---------- Q56: choose 4 of A-F; (1) A -> not B; (2) C,E same status
cnt=[]
for sel in itertools.combinations('ABCDEF',4):
    s=set(sel)
    if 'A' in s and 'B' in s: continue
    if ('C' in s)!=('E' in s): continue
    cnt.append(''.join(sel))
print('Q56 count',len(cnt),cnt)

# ---------- Q60: week Mon..Sun, each day: None / 'S' swim / 'R' run(gym)
# 3 swims + 2 gym(run) sessions, at most one activity per day ((1) no swim+run same day)
# (2) no same sport on consecutive days; (3) exactly one weekend day with exercise
# (4) pool closed Monday; Friday cannot run
days=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
sols=[]
for assign in itertools.product([None,'S','R'],repeat=7):
    if assign.count('S')!=3 or assign.count('R')!=2: continue
    if assign[0]=='S' or assign[4]=='R': continue
    if sum(1 for d in (5,6) if assign[d]) !=1: continue
    if any(assign[i] and assign[i]==assign[i+1] for i in range(6)): continue
    sols.append(assign)
print('Q60 solutions:',len(sols))
for s in sols: print('  ',' '.join('%s:%s'%(d,a or '-') for d,a in zip(days,s)))
A=any(s[6]=='R' for s in sols)
B=all(s[0]=='R' for s in sols)
C=all(set(i for i,a in enumerate(s) if a=='S')<= {3,4,6} for s in sols)
Dv=all((s[1]!='R') or (s[3]=='R') for s in sols)
print('A (possible run on Sun):',A,' B (must run Mon):',B,' C (swim only Thu/Fri/Sun):',C,' D (Tue run -> Thu run):',Dv)
# variant: also treat the gym as generic (gym = run) - same as above; variant with Sunday->Monday wrap
sols2=[s for s in sols if not (s[6] and s[6]==s[0])]
print('with week wrap Sun->Mon also forbidden:',len(sols2))
