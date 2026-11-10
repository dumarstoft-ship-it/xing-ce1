import itertools
# P13
E=[('水草','螺'),('水草','鲫鱼'),('螺','鲫鱼'),('浮游藻类','浮游动物'),('浮游藻类','虾'),('浮游动物','虾'),('浮游动物','小鱼'),('虾','小鱼'),('虾','鳜鱼'),('小鱼','鳜鱼'),('小鱼','白鹭'),('鲫鱼','鳜鱼'),('鲫鱼','白鹭')]
succ={}
for a,b in E: succ.setdefault(a,[]).append(b)
nodes={x for e in E for x in e}
prey_of={b for a,b in E}
producers=[n for n in nodes if n not in prey_of]
chains=[]
def dfs(p):
    s=succ.get(p[-1],[])
    if not s: chains.append(p); return
    for n in s: dfs(p+[n])
for pr in producers: dfs([pr])
print('producers',producers,'chains',len(chains))
lv=set()
for c in chains:
    if '小鱼' in c: lv.add(c.index('小鱼')+1)
print('小鱼 trophic levels',lv)
print('白鹭 eats 鳜鱼?',('鳜鱼','白鹭') in E,'鳜鱼 eats 白鹭?',('白鹭','鳜鱼') in E)
# P24
P=['甲','乙','丙','丁','戊','己']
res=set()
for done in itertools.product([0,1],repeat=6):
    d=dict(zip(P,done))
    s={'甲':not d['甲'],'乙':bool(d['丙']),'丙':not any(done),'丁':not bool(d['丙']),'戊':bool(d['乙']),'己':(d['甲']+d['丙'])==1}
    if sum(1 for v in s.values() if not v)==2:
        res.add((d['甲'],d['乙'],d['丙'],d['甲']+d['乙']+d['丙']))
print('P24 (甲,乙,丙,count):',res)
# P25
for w in ['甲','乙','丙']:
    pr=[w!='甲', w=='乙', w!='丙']
    print('P25 winner',w,'correct',sum(pr))
