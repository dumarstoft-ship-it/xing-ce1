# Enumeration checks for Q55 and Q60 (and a truth-table check for Q51)
import itertools

print('== Q55 ==')
people=['王','李','张','赵','刘']; acts=['游','影','工']   # 周边游 / 看电影 / 做手工
sols=[]
for ch in itertools.product(acts,repeat=5):
    c=dict(zip(people,ch))
    cnt={a:list(ch).count(a) for a in acts}
    if any(not(1<=cnt[a]<=2) for a in acts): continue
    if c['赵']!='工': continue
    if (c['张'] in ('工','影') or c['赵'] in ('工','影')) and c['王']!='游': continue
    if (c['赵'] in ('游','影') or c['刘'] in ('游','影')) and not (c['王']=='工' or c['李']=='工'): continue
    if (c['刘']=='工' or c['张']=='游') and not (c['李']=='影' and c['赵']=='影'): continue
    sols.append(c)
for s in sols: print(s)
opts={'A 刘看电影':lambda c:c['刘']=='影','B 王周边游':lambda c:c['王']=='游','C 李做手工':lambda c:c['李']=='工','D 张看电影':lambda c:c['张']=='影'}
for k,f in opts.items(): print(k,'always' if all(f(s) for s in sols) else 'NOT always')

print('== Q60 ==')
names=['猎豹','兔子','狮子','马','羚羊','狼','鹿']
sols=[]
for perm in itertools.permutations(range(1,8)):
    r=dict(zip(names,perm))
    if r['猎豹']!=4: continue
    if not (r['狮子']<r['兔子']<r['马']): continue
    if not (r['羚羊']<r['猎豹']<r['狼']): continue
    if (r['狮子']==2 or r['羚羊']==3) and r['狼']!=1: continue
    if (r['羚羊']==2 or r['兔子']==6) and r['马']!=3: continue
    sols.append(r)
for s in sols: print(sorted(s.items(),key=lambda kv:kv[1]))
opts={'A 兔子比狼快':lambda r:r['兔子']<r['狼'],'B 猎豹比兔子快':lambda r:r['猎豹']<r['兔子'],
      'C 狮子比鹿快':lambda r:r['狮子']<r['鹿'],'D 羚羊比狮子快':lambda r:r['羚羊']<r['狮子']}
for k,f in opts.items(): print(k,'possible' if any(f(s) for s in sols) else 'IMPOSSIBLE')

print('== Q51 ==')
# Z: 转化为发展优势; N: 满足需要; G: 加快建设/推动高质量发展; F: 发挥四种作用
# premises: N->Z (关键=必要条件), G->Z (必由之路), ~F->~Z
def imp(p,q): return (not p) or q
worlds=[w for w in itertools.product([0,1],repeat=4) if imp(w[1],w[0]) and imp(w[2],w[0]) and imp(not w[3], not w[0])]
Z,N,G,F=0,1,2,3
checks={'A N->G':lambda w:imp(w[N],w[G]),'B G->F':lambda w:imp(w[G],w[F]),'C F->Z':lambda w:imp(w[F],w[Z]),'D ~G->~Z':lambda w:imp(not w[G],not w[Z])}
for k,f in checks.items(): print(k,'valid' if all(f(w) for w in worlds) else 'not valid')
