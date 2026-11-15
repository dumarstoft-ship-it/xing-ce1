from itertools import permutations, product
print('=== Q51 (bijection interpretation) ===')
P=['小全','大陈','小吴','大刘']; S=['游泳','跳水','水球','赛艇']
def ok51(a):
    c1 = (not a['小全']=='游泳') or (a['大陈']!='跳水')          # 小全游泳 -> 大陈不跳水
    c2 = (not a['大刘']=='水球') or (a['大陈']=='跳水')          # 大刘水球 -> 大陈跳水
    c3 = (a['小吴']=='游泳') != (a['小全']=='游泳')
    c4 = (a['小全']!='赛艇') != (a['大刘']=='水球')
    return c1 and c2 and c3 and c4
sols=[dict(zip(P,p)) for p in permutations(S) if ok51(dict(zip(P,p)))]
print('all models:',len(sols))
for s in sols: print('  ',s)
opts={'A':lambda a:a['小全']=='赛艇','B':lambda a:a['大陈']!='跳水','C':lambda a:a['大陈']=='水球','D':lambda a:a['大刘']!='水球'}
for k,f in opts.items():
    m=[s for s in sols if f(s)]
    print(k,'models',len(m),'all 小吴游泳?',all(s['小吴']=='游泳' for s in m) if m else 'NO MODEL')
print('=== Q51 (each person any subset of sports, non-exclusive) ===')
# variables: practice[p][s] boolean
import itertools
cnt=0
res={k:[0,0] for k in opts}
for bits in product([0,1],repeat=16):
    pr={p:{s:bits[i*4+j] for j,s in enumerate(S)} for i,p in enumerate(P)}
    c1=(not pr['小全']['游泳']) or (not pr['大陈']['跳水'])
    c2=(not pr['大刘']['水球']) or pr['大陈']['跳水']
    c3=pr['小吴']['游泳']!=pr['小全']['游泳']
    c4=(not pr['小全']['赛艇'])!=bool(pr['大刘']['水球'])
    if not(c1 and c2 and c3 and c4): continue
    for k,f in {'A':lambda:pr['小全']['赛艇'],'B':lambda:not pr['大陈']['跳水'],'C':lambda:pr['大陈']['水球'],'D':lambda:not pr['大刘']['水球']}.items():
        if f():
            res[k][0]+=1
            if pr['小吴']['游泳']: res[k][1]+=1
for k,(n,y) in res.items(): print(k,'models',n,'with 小吴游泳',y,'-> forced' if n==y and n>0 else '')

print('=== Q52 ===')
people=['张','王','李','赵','钱','孙']; aw='甲乙丙丁'
sols=[]
for a in product(aw,repeat=6):
    d=dict(zip(people,a))
    cnt={x:a.count(x) for x in aw}
    if any(not(1<=cnt[x]<=2) for x in aw): continue
    if not cnt['乙']>cnt['甲']: continue
    if not cnt['丁']>cnt['丙']: continue
    if (d['李']=='甲' or d['赵']=='甲') and d['王']!='丁': continue
    if any(d[p]=='乙' for p in ['张','李','赵']):
        if [p for p in people if d[p]=='丁']!=['钱']: continue
    if d['孙']!='丙': continue
    sols.append(d)
print(len(sols),sols)
o={'A':lambda d:d['张']=='丙','B':lambda d:d['赵']=='乙' and d['钱']=='乙','C':lambda d:d['王']=='丁' and d['李']=='丁','D':lambda d:d['李']=='丁' and d['赵']=='丁'}
for k,f in o.items(): print(k,[f(d) for d in sols])

print('=== Q53 ===')
vals={'甲':9472,'乙':9496,'丙':9480,'丁':9502}
for est in vals:
    others=[p for p in vals if p!=est]
    for perm in permutations([-17,-9,13]):
        Ts={vals[p]-e for p,e in zip(others,perm)}
        if len(Ts)==1: print('estimator',est,'true count',Ts.pop(),dict(zip(others,perm)))

print('=== Q54 ===')
for r in permutations([1,2,3,4]):
    rk=dict(zip('甲乙丙丁',r))
    g1=(rk['乙']!=2) or (rk['甲']==3)
    g2=(rk['丙']==1) or (rk['丁']!=4)
    g3=rk['甲']!=3
    g4=rk['丙']==2
    if [g1,g2,g3,g4].count(True)==1: print(rk,[g1,g2,g3,g4])
